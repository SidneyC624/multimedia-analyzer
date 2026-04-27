from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import os
import uuid
from datetime import datetime

app = FastAPI()

jobs = {}

@app.get("/")
def read_root():
    return {"status": "Multimedia API is online"}


# variable: file -> type: UploadFile
# = File(...) -> pulled from form data of request, required otherwise send 422 Unprocessable Entity error
@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):

    job_id = str(uuid.uuid4())

    #----- saving file to disk -----
    if file.content_type not in ["video/mp4", "audio/mpeg"]:
        return {"error": "Sorry, I only accept media files"}

    uploads = Path("uploads")
    uploads.mkdir(exist_ok=True)
    destination_path = uploads / f"{job_id}_{file.filename}"

    # videos and audio are not plain text, thus written in binary mode
    try:
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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
    
    jobs[job_id] = {
        "status": "pending",
        "file_path": str(destination_path),
        "timestamp": datetime.fromtimestamp(destination_path.stat().st_mtime)
    }

    return {"job_id": job_id}