from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uuid
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    url: str
    timestamp: datetime

jobs = {}

@app.get("/")
def read_root():
    return {"status": "Multimedia API is online"}


@app.post("/submit-url", response_model=JobResponse)
async def upload_video(payload: URLRequest):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    job_id = str(uuid.uuid4())
    timestamp = datetime.now()
    
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "url": url,
        "timestamp": timestamp
    }
    jobs[job_id] = job_data

    return job_data


@app.get("/status/{job_id}", response_model=JobResponse)
def check_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job