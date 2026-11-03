from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import uuid
import json
from datetime import datetime

from pipeline import run_lecture_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

slides_dir = Path("slides")
slides_dir.mkdir(exist_ok=True)
app.mount("/slides", StaticFiles(directory="slides"), name="slides")

class URLRequest(BaseModel):
    url: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    url: str
    timestamp: datetime
    result: dict | None = None

jobs = {}

def process_pipeline_job(job_id: str, url: str):
    """Executes the pipeline in a background worker"""
    try:
        jobs[job_id]["status"] = "processing"

        run_lecture_pipeline(
            url=url,
            output_json_path=f"output/{job_id}_synchronized.json",
            study_guide_output_path=f"output/{job_id}_study_guide.json"
        )

        # Reading generated study guide and synchronized data (slides and transcript)
        study_guide_path = Path(f"output/{job_id}_study_guide.json")
        sync_path = Path(f"output/{job_id}_synchronized.json")

        with open(study_guide_path, "r", encoding="utf-8") as f:
            guide_data = json.load(f)

        with open(sync_path, "r", encoding="utf-8") as f:
            sync_data = json.load(f)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "study_guide": guide_data,
            "slides_metadata": sync_data
        }

    except Exception as e:
        print(f"Error executing pipeline for job {job_id}: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.get("/")
def read_root():
    return {"status": "Multimedia API is online"}


@app.post("/submit-url", response_model=JobResponse)
async def upload_video(payload: URLRequest, background_tasks: BackgroundTasks):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    job_id = str(uuid.uuid4())
    timestamp = datetime.now()
    
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "url": url,
        "timestamp": timestamp,
        "result": None
    }
    jobs[job_id] = job_data

    background_tasks.add_task(process_pipeline_job, job_id, url)

    return job_data


@app.get("/status/{job_id}", response_model=JobResponse)
def check_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job