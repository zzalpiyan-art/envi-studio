from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone

app = FastAPI(title="ENVI - AI Video Production Studio")

WORKERS = [
    {"id": 1, "name": "Si Kurir"},
    {"id": 2, "name": "Si Pemburu Momen"},
    {"id": 3, "name": "Si Juru Tulis"},
    {"id": 4, "name": "Si Editor"},
    {"id": 5, "name": "Si Copywriter"},
    {"id": 6, "name": "Si QC"}
]

jobs = {}

class JobCreate(BaseModel):
    youtube_url: str

@app.get("/")
def home():
    return {
        "app": "ENVI - AI Video Production Studio",
        "status": "running"
    }

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": "ENVI - AI Video Production Studio"
    }

@app.get("/api/workers")
def get_workers():
    return WORKERS

@app.post("/api/jobs")
def create_job(data: JobCreate):
    job_id = str(uuid4())

    job = {
        "id": job_id,
        "youtube_url": data.youtube_url,
        "status": "Todo",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message": "Job berhasil dibuat"
    }

    jobs[job_id] = job
    return job

@app.get("/api/jobs")
def get_jobs():
    return list(jobs.values())

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        return {"error": "Job tidak ditemukan"}

    return jobs[job_id]
