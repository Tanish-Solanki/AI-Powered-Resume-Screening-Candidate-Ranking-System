from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.dependencies import get_db
from app.models.user import User
from app.models.job import JobDescription
from app.models.candidate import Candidate
from app.models.screening import CandidateScore

router = APIRouter(prefix="/analytics", tags=["dashboard metadata"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    total_jobs = db.query(func.count(JobDescription.id)).scalar()
    total_candidates = db.query(func.count(Candidate.id)).scalar()
    total_screenings = db.query(func.count(CandidateScore.id)).scalar()
    
    avg_score = db.query(func.avg(CandidateScore.final_score)).scalar() or 0.0
    
    return {
        "metrics": {
            "total_users": total_users,
            "total_jobs": total_jobs,
            "total_candidates": total_candidates,
            "total_screenings": total_screenings,
            "average_candidate_score": round(avg_score, 2)
        }
    }

@router.get("/candidates-overview")
def get_candidate_statistics(db: Session = Depends(get_db)):
    return {
        "status": "Healthy",
        "message": "Detailed demographic and performance breakdown available here in production"
    }
