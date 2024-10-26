from openai import OpenAI
from typing import List, Dict
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import instructor
import json
import time

load_dotenv('.env')
llm_model = os.getenv('LLM_MODEL')

class JobDescription(BaseModel):
    education: List[str]
    work_experience: List[str]
    skills: List[str]
    projects: List[str]
    certifications: List[str]
    additional_info: List[str]
    job_requirements: List[str]

class LLMScreener(BaseModel):
    is_fit: bool
    reasoning: Dict[str, str]  # Modified to hold reasoning per category

client = instructor.from_openai(OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama',
),
    mode=instructor.Mode.JSON
)

def divide_into_overlapping_blocks(text, block_size, overlap):
    txt_list = text.split('\n')
    
    blocks = []
    start = 0
    
    while start < len(txt_list):
        block = txt_list[start:start + block_size]
        blocks.append('\n'.join(block))
        
        start += (block_size - overlap)
        
    return blocks

def summarize_chain(text):
    llm = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama'
    )

    # Break the text into smaller chunks
    chunks = divide_into_overlapping_blocks(text, 1500, 300)  # Use smaller chunks to fit comfortably within context window

    while len(text) > 4096:
        resp = ""
        for chunk in chunks:
            retries = 3
            while retries > 0:
                try:
                    # Request a summary of the chunk with an explicit token limit
                    result = llm.chat.completions.create(
                        model="llama3",
                        max_retries=6,
                        temperature=0.0,
                        max_tokens=500,  # Limit the size of the output to make the summarization manageable
                        messages=[
                            {
                                "role": "system",
                                "content": f"Summarize the following text. Extract all key information while keeping the summary concise: {chunk}"
                            }
                        ]
                    )
                    resp += "\n" + result
                    break
                except Exception as e:
                    retries -= 1
                    if retries == 0:
                        print(f"Error after retries: {e}. Handling gracefully.")
                        return "Summary could not be completed due to an error."
                    time.sleep(2)

        text = resp.strip()
        # Re-chunk the summarized text if needed
        if len(text) > 4096:
            chunks = divide_into_overlapping_blocks(text, 1500, 300)

    return text


def create_JD_tags(JD_text):
    retries = 3
    while retries > 0:
        try:
            return json.loads(
                client.chat.completions.create(
                    model="llama3",
                    max_retries=6,
                    temperature=0.2,
                    messages=[{
                        "role": "system", 
                        "content": (
                            f"You are a part of an NLP resume screener. Divide your task into two."
                            f" First, extract keywords from the following Job Description and categorize them as"
                            f" Education, Work Experience, Skills, Certifications, Work Projects, and Additional Info."
                            f" STRICTLY ensure that ALL keywords are a maximum of TWO words. Avoid phrases, avoid stopwords, keep it concise."
                            f" For example, instead of 'excellent troubleshooting skills', use 'troubleshooting'."
                            f" Also ensure to separate compound keywords ONLY WHERE NECESSARY, e.g., 'html5/css3/javascript' becomes 'html5', 'css3', 'javascript'."
                            f" Second, list the strict requirements for the job, including minimum experience."
                            f" Leave any field blank if no data is available."
                            f" Job description: {JD_text}"
                        )
                    }],
                    response_model=JobDescription
                ).model_dump_json(indent=4)
            )
        except Exception as e:
            retries -= 1
            if retries == 0:
                print(f"Error after retries: {e}. Handling gracefully.")
                return {
                    "education": "",
                    "work_experience": "",
                    "skills": "",
                    "certifications": "",
                    "projects": "",
                    "additional_info": ""
                }
            time.sleep(2)

def assess_candidate(job_desc, resume_text):
    job_reqs = job_desc['job_requirements']
    del job_desc['job_requirements']

    retries = 3
    while retries > 0:
        try:
            return json.loads(
                client.chat.completions.create(
                    model=llm_model,
                    max_retries=6,
                    messages=[{"role": "system", "content": 
                               summarize_chain(f"You are part of a resume screener. Based on the following job requirements and the resume provided, determine if the candidate is fit for the job. Furthermore, from the following list of categories, list down all the categories that the candidate is ineligible for on the basis of the job description.\n Job requirements: {job_reqs}.\n Job Categories: {job_desc}.\n Resume: {resume_text}.\n")}],
                    response_model=LLMScreener
                ).model_dump_json(indent=2)
            )
        except Exception as e:
            retries -= 1
            if retries == 0:
                print(f"Error after retries: {e}. Handling gracefully.")
                return {"is_fit": False, "reasoning": "Candidate assessment could not be completed due to an error."}
            time.sleep(2)

if __name__ == "__main__":
    pass

