import os
from uuid import uuid4
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./envi.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

options = {}
if DATABASE_URL.startswith("sqlite"):
    options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **options)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    source_url = Column(String, nullable=False)
    status = Column(String, default="Todo")
    stage = Column(String, default="Menunggu pemrosesan")
    candidates = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ENVI AI Video Production Studio",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def validate_youtube_url(value: str):
    parsed = urlparse(value.strip())
    hosts = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be"
    }

    if parsed.scheme != "https" or parsed.hostname not in hosts:
        raise HTTPException(
            status_code=400,
            detail="Masukkan URL YouTube HTTPS yang valid."
        )

    if parsed.hostname == "youtu.be":
        if not parsed.path.strip("/"):
            raise HTTPException(400, "ID video tidak ditemukan.")
    elif parsed.path == "/watch":
        if not parsed.query or not any(
            part.startswith("v=") for part in parsed.query.split("&")
        ):
            raise HTTPException(400, "ID video tidak ditemukan.")
    elif not parsed.path.startswith(("/shorts/", "/live/")):
        raise HTTPException(400, "Format URL YouTube tidak dikenali.")


class CreateJob(BaseModel):
    url: str = Field(min_length=10, max_length=500)
    candidate_count: int = Field(default=3, ge=2, le=5)


@app.get("/")
def home():
    return {
        "app": "ENVI",
        "version": "1.0.0",
        "status": "online",
        "workers": [
            "Si Kurir",
            "Si Pemburu Momen",
            "Si Juru Tulis",
            "Si Editor",
            "Si Copywriter",
            "Si QC"
        ]
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/jobs", status_code=201)
def create_job(data: CreateJob):
    validate_youtube_url(data.url)

    job_id = str(uuid4())
    candidates = [
        {
            "id": f"{job_id}-clip-{i+1}",
            "name": f"Kandidat Klip {i+1}",
            "status": "Todo",
            "progress": 0,
            "stage": "Menunggu analisis",
            "start": None,
            "end": None,
            "transcript": None,
            "caption": None,
            "output": None
        }
        for i in range(data.candidate_count)
    ]

    db = SessionLocal()
    try:
        job = Job(
            id=job_id,
            source_url=data.url.strip(),
            status="Todo",
            stage="Menunggu pemrosesan",
            candidates=candidates
        )
        db.add(job)
        db.commit()

        return {
            "success": True,
            "job_id": job_id,
            "message": "Quest berhasil dibuat.",
            "candidates": candidates
        }
    finally:
        db.close()


@app.get("/api/jobs")
def get_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(Job).order_by(Job.created_at.desc()).all()
        return [
            {
                "id": job.id,
                "url": job.source_url,
                "status": job.status,
                "stage": job.stage,
                "candidates": job.candidates,
                "created_at": (
                    job.created_at.isoformat()
                    if job.created_at else None
                )
            }
            for job in jobs
        ]
    finally:
        db.close()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            raise HTTPException(404, "Quest tidak ditemukan.")

        return {
            "id": job.id,
            "url": job.source_url,
            "status": job.status,
            "stage": job.stage,
            "candidates": job.candidates,
            "created_at": (
                job.created_at.isoformat()
                if job.created_at else None
            )
        }
    finally:
        db.close()
