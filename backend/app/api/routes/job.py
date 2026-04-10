from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db
from app.models.job import JobDescription
from app.schemas.job import JobDescriptionCreate, JobDescriptionOut

router = APIRouter(prefix="/jobs", tags=["job descriptions"])

# Note: In production, inject current_user logic via dependency
# Fake user dependency for boilerplate
def get_current_user_id() -> int:
    return 1

@router.post("/", response_model=JobDescriptionOut, status_code=status.HTTP_201_CREATED)
def create_job_description(
    job_in: JobDescriptionCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    job_obj = JobDescription(
        title=job_in.title,
        description=job_in.description,
        created_by=user_id
    )
    db.add(job_obj)
    db.commit()
    db.refresh(job_obj)
    return job_obj

@router.get("/", response_model=List[JobDescriptionOut])
def read_job_descriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(JobDescription).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobDescriptionOut)
def read_job_description(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_description(
    job_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Description not found")
    
    if job.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
        
    db.delete(job)
    db.commit()
    return None
