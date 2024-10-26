# app.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
import shutil
import json
from app.main import rank_resumes, jd_collection, add_JD_tags
from app.utils import parse_resume

EMPLOYEE_FOLDER = "employee_docs"  # Ensure consistency with main.py
JD_FOLDER = "jd_docs"

app = FastAPI()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the EMPLOYEE_FOLDER exists on startup
if not os.path.exists(EMPLOYEE_FOLDER):
    os.makedirs(EMPLOYEE_FOLDER)

# Home Route
@app.get("/")
async def home():
    return {"message": "Welcome to the Resume Parser"}

# Resume Routes
@app.post("/resumes")
async def upload_resumes(resumes: List[UploadFile] = File(...)):
    supported_formats = ['.pdf', '.docx', '.txt', '.doc']
    for file in resumes:
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")
        file_path = os.path.join(EMPLOYEE_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    return {"message": "Resumes uploaded successfully!"}

@app.delete("/resumes")
async def delete_resumes(resumes: List[str]):
    not_found_files = []
    for file_name in resumes:
        total_file_path = os.path.join(EMPLOYEE_FOLDER, file_name)
        if os.path.exists(total_file_path):
            os.remove(total_file_path)
        else:
            not_found_files.append(file_name)
    if not_found_files:
        raise HTTPException(status_code=404, detail=f"Files not found: {', '.join(not_found_files)}")
    return {"message": "Resumes deleted successfully!"}

@app.delete("/resumes/all")
async def delete_all_resumes():
    if os.path.exists(EMPLOYEE_FOLDER):
        shutil.rmtree(EMPLOYEE_FOLDER)  # Remove directory and contents
    os.makedirs(EMPLOYEE_FOLDER)  # Recreate directory
    return {"message": "All resumes deleted successfully!"}

@app.get("/resumes/scores")
async def get_resume_scores(
    include_fit: bool = Query(False, description="Include fitness assessment in ranking"),
    criteria: str = Query("keyword", description="Scoring criteria: 'keyword' or 'cosine'")
):
    """
    Retrieves and ranks resumes based on the specified weights, fitness assessment, and criteria.
    
    - **include_fit**: If set to True, performs a fitness assessment using LLM.
    - **criteria**: Determines the scoring method ('keyword' or 'cosine').
    """
    file_paths = [os.path.join(EMPLOYEE_FOLDER, file_path) for file_path in os.listdir(EMPLOYEE_FOLDER)]
    
    if not file_paths:
        raise HTTPException(status_code=404, detail="No resumes uploaded")

    # Validate criteria
    if criteria not in ["keyword", "cosine"]:
        raise HTTPException(status_code=400, detail="Invalid criteria. Choose 'keyword' or 'cosine'.")

    # Load weights from weights.json or use default weights
    if os.path.exists('weights.json'):
        with open('weights.json', 'r') as f:
            weights = json.load(f)
    else:
        # Default weights if weights.json does not exist
        weights = {
            "education": 0.15,
            "work_experience": 0.30,
            "skills": 0.25,
            "certifications": 0.10,
            "projects": 0.10,
            "additional_info": 0.10
        }

    try:
        # Rank resumes using the updated rank_resumes function
        ranked_results = rank_resumes(file_paths, weights, include_fit=include_fit, criteria=criteria)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # Format the results into a list of dictionaries with feedback
    formatted_results = [
        {
            "resume": os.path.basename(resume_path),
            "score": score
        }
        for resume_path, score in ranked_results
    ]

    return {"results": formatted_results}

# Job Description (JD) Routes
@app.post("/jd")
async def create_job_description(jd_files: List[UploadFile] = File(...)):
    if not os.path.exists(JD_FOLDER):
        os.makedirs(JD_FOLDER)
    for file in jd_files:
        file_path = os.path.join(JD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        jd_text = parse_resume(file_path)
        add_JD_tags(jd_text)
    return {"message": "Job Descriptions uploaded successfully!"}

class JobDescriptionUpdate(BaseModel):
    category: str
    data: List[str]

@app.put("/jd")
async def update_job_description(updated_job_description: JobDescriptionUpdate):
    category = updated_job_description.category
    data = updated_job_description.data
    result = jd_collection.update_one({"category": category}, {"$set": {"data": data}})
    if result.matched_count:
        return {"message": "Job description updated successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Category not found!")

@app.delete("/jd")
async def delete_job_description(category: str = Query(..., description="Category of the job description to delete")):
    result = jd_collection.delete_one({"category": category})
    if result.deleted_count:
        return {"message": "Job description deleted successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Category not found!")

@app.get("/jd/all")
async def get_job_descriptions():
    job_descriptions = list(jd_collection.find({}, {"_id": 0}))
    return {"job_descriptions": job_descriptions}

@app.delete("/jd/all")
async def delete_all_job_descriptions():
    jd_collection.delete_many({})
    return {"message": "All job descriptions deleted successfully!"}

class AppendJDRequest(BaseModel):
    category: str
    jds: List[str]

@app.post("/jd/sub")
async def append_jds(request: AppendJDRequest):
    category = request.category
    new_jds = request.jds

    jd_entry = jd_collection.find_one({"category": category})

    if jd_entry:
        existing_jds = jd_entry["data"]
        updated_jds = list(set(existing_jds + new_jds))  # Avoid duplicates

        jd_collection.update_one(
            {"category": category},
            {"$set": {"data": updated_jds}}
        )
        return {"message": "Job Descriptions appended successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Category not found!")

class RemoveJDRequest(BaseModel):
    category: str
    jds: List[str]

@app.delete("/jd/sub")
async def remove_jds(request: RemoveJDRequest):
    category = request.category
    jds_to_remove = request.jds

    jd_entry = jd_collection.find_one({"category": category})

    if jd_entry:
        existing_jds = jd_entry["data"]
        updated_jds = [jd for jd in existing_jds if jd not in jds_to_remove]

        jd_collection.update_one(
            {"category": category},
            {"$set": {"data": updated_jds}}
        )
        return {"message": "Job Descriptions removed successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Category not found!")

@app.get("/jd/{category}")
async def get_job_description_by_category(category: str):
    jd_entry = jd_collection.find_one({"category": category}, {"_id": 0})
    if jd_entry:
        return jd_entry
    else:
        raise HTTPException(status_code=404, detail="Category not found!")

# Weights Routes
class Weights(BaseModel):
    weights: Dict[str, float]

@app.post("/weights")
async def set_weights(weights_data: Weights):
    with open('weights.json', 'w') as f:
        json.dump(weights_data.weights, f, indent=4)
    return {"message": "Weights set successfully!"}

@app.get("/weights")
async def get_weights():
    if os.path.exists('weights.json'):
        with open('weights.json', 'r') as f:
            weights = json.load(f)
        return {"weights": weights}
    else:
        raise HTTPException(status_code=404, detail="Weights file not found!")
