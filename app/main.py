# main.py

from dotenv import load_dotenv
from pymongo import MongoClient
from app.utils import parse_resume
from app.llm import create_JD_tags, assess_candidate
from sentence_transformers import SentenceTransformer, util
import json
import re
import os
import spacy

load_dotenv('.env')
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# MongoDB setup
client = MongoClient(os.getenv('MONGODB_URI'))
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions

# Load NLP models
nlp = spacy.load("en_core_web_md")

# Initialize SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Using SentenceTransformer for embeddings

def get_job_description():
    jd_docs = list(jd_collection.find({}))
    return {doc['category']: doc['data'] for doc in jd_docs}

def add_JD_tags(JD_text):
    tags_and_reqs = create_JD_tags(JD_text)

    # Add tags to the tags collection uniquely
    for category, tags in tags_and_reqs.items():
        modified_tags = [tag.lower().replace('_', ' ') for tag in tags]
        jd_collection.update_one(
            {"category": category},  # Ensure correct category
            {"$addToSet": {"data": {"$each": modified_tags}}},  # Add tags only if they are not already present
            upsert=True  # Insert new category if it doesn't exist
        )

def calculate_keyword_score(resume_text, weights):
    total_score = 0
    
    # Normalize the resume text
    resume_text = " ".join([token.text.lower() for token in nlp(resume_text) if not token.is_space and not token.is_punct])
    
    # Retrieve all job descriptions
    job_descriptions = get_job_description()
    
    # Iterate through each category and calculate the score
    for category, weight in weights.items():
        keywords = job_descriptions.get(category, [])
        match_indicator = 1 if any(re.search(rf'\b{keyword}\b', resume_text, re.IGNORECASE) for keyword in keywords) else 0
        total_score += (weight * match_indicator)  # Sum the weighted scores

    return total_score  # Return total score without normalization

def calculate_similarity_score(resume_text, weights):
    total_score = 0
    feedback = {}
    
    # Retrieve all job descriptions
    job_descriptions = get_job_description()
    
    # Calculate embeddings for the resume
    resume_embedding = model.encode(resume_text, convert_to_tensor=True, show_progress_bar=False)
    
    for category, weight in weights.items():
        jd_texts = job_descriptions.get(category, [])
        if not jd_texts:
            continue  # Skip if no JDs for the category
        
        # Aggregate JD texts into a single string
        jd_combined = " ".join(jd_texts)
        
        # Calculate embedding for JD
        jd_embedding = model.encode(jd_combined, convert_to_tensor=True, show_progress_bar=False)
        
        # Compute cosine similarity
        similarity = util.cos_sim(jd_embedding, resume_embedding).item()
        similarity = max(0, similarity)  # Ensure non-negative
        
        # Apply weight
        weighted_similarity = similarity * weight
        total_score += weighted_similarity
        feedback[category] = similarity  # Store similarity for feedback
    
    return total_score  # Return total similarity score

def rank_resumes(resume_files, weights, include_fit=False, criteria="keyword"):
    """
    Rank resumes based on the selected criteria: 'keyword' or 'cosine'.
    
    :param resume_files: List of file paths to resumes.
    :param weights: Dictionary containing weights for each category.
    :param include_fit: Boolean indicating whether to perform fitness assessment.
    :param criteria: String indicating the scoring criteria ('keyword' or 'cosine').
    :return: List of tuples containing resume file path and its score.
    """
    ranked_resumes = []
    for resume_file in resume_files:
        resume_text = parse_resume(resume_file)
        candidate_is_fit = True
        if include_fit:
            job_description = get_job_description()
            inferenced_resume = assess_candidate(job_description, resume_text)
            candidate_is_fit = inferenced_resume['is_fit']
        
        if candidate_is_fit:
            if criteria == "keyword":
                score = calculate_keyword_score(resume_text, weights)
            elif criteria == "cosine":
                score = calculate_similarity_score(resume_text, weights)
            else:
                raise ValueError("Invalid criteria. Choose 'keyword' or 'cosine'.")
            ranked_resumes.append((resume_file, score))
        else:
            print(f"Candidate {resume_file} not fit.")
            ranked_resumes.append((resume_file, 0.1))  # Assign low score if not fit

    return ranked_resumes

# Example usage (for testing purposes)
if __name__ == "__main__":
    # print(rank_resumes(
    #     [f'uploaded_resumes/{file_path}' for file_path in os.listdir('uploaded_resumes')], 
    #     {
    #         "education": 0.15,
    #         "work_experience": 0.30,
    #         "skills": 0.25,
    #         "certifications": 0.10,
    #         "projects": 0.10,
    #         "additional_info": 0.10
    #     }, 
    #     include_fit=False, 
    #     criteria="cosine"  # Change to "cosine" to use cosine similarity-based scoring
    # ))
    pass
