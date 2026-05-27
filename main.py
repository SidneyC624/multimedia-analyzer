from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import shutil
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

class UploadResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    timestamp: datetime

jobs = {}

@app.get("/")
def read_root():
    return {"status": "Multimedia API is online"}


# variable: file -> type: UploadFile
# = File(...) -> pulled from form data of request, required otherwise send 422 Unprocessable Entity error
@app.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    print(f"DEBUG: Filename: {file.filename}, Content-Type: {file.content_type}")
    job_id = str(uuid.uuid4())

    #----- saving file to disk -----
    if file.content_type not in ["video/mp4", "audio/mpeg", "video/matroska"]:
        raise HTTPException(
            status_code=400,
            detail="Sorry, I only accept media files (MP4, MP3, MKV)"
        )

    uploads = Path("uploads")
    uploads.mkdir(exist_ok=True)
    destination_path = uploads / f"{job_id}_{file.filename}"

    # videos and audio are not plain text, thus written in binary mode
    try:
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_stats = destination_path.stat()
        timestamp = datetime.fromtimestamp(file_stats.st_mtime)
        

    except OSError as e:
        # error code for "No space left on device"
        if e.errno == 28:
            raise HTTPException(status_code=507, detail="Server storage is full.")
        raise HTTPException(status_code=500, detail=f"Disk error: {str(e)}")
    
    except Exception as e:
        # connection interruptions or unexpected errors
        raise HTTPException(status_code=400, detail="File upload interrupted or failed")
    
    finally:
        await file.close()
    #--------------------------------
    
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "filename": file.filename,
        "timestamp": timestamp
    }
    jobs[job_id] = job_data

    return job_data


@app.get("/status/{job_id}", response_model=UploadResponse)
def check_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job