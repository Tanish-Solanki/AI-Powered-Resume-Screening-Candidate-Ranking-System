from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db
from app.models.job import JobDescription
from app.models.candidate import Candidate
from app.models.screening import CandidateScore
from app.schemas.screening import CandidateScoreOut
from app.utils.resume_parser import extract_resume_sections
from app.ml.skill_extractor import extract_skills
from app.ml.ranking_engine import rank_candidates

router = APIRouter(prefix="/candidates", tags=["scoring & ranking"])

@router.post("/{job_id}/rank", response_model=List[CandidateScoreOut])
def trigger_ranking_pipeline(job_id: int, db: Session = Depends(get_db)):
    """
    Executes the AI NLP Ranking Engine against all available candidates 
    for a specified Job Description.
    """
    # Fetch JD
    jd = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
        
    # Standard JD data format mapping
    jd_skills = extract_skills(jd.description).get("technical_skills", [])
    jd_data = {
        "raw_text": jd.description,
        "required_skills": jd_skills,
        "experience_requirements": jd.description # fallback contextually
    }
    
    # Fetch Candidate pool
    candidates = db.query(Candidate).all()
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates found in database to rank")
        
    candidate_payloads = []
    for cand in candidates:
        cand_sections = extract_resume_sections(cand.extracted_text or "")
        cand_skills = extract_skills(cand.extracted_text or "")
        candidate_payloads.append({
            "candidate_id": cand.id,
            "raw_text": cand.extracted_text,
            "sections": cand_sections,
            "extracted_skills": cand_skills
        })
        
    # Execute ML Engine
    ranked_results = rank_candidates(candidate_payloads, jd_data)
    
    # Save to Database as CandidateScore objects
    # Wipe previous scores for this JD to prevent duplication
    db.query(CandidateScore).filter(CandidateScore.jd_id == job_id).delete()
    db.commit()
    
    response_payload = []
    for rank_data in ranked_results:
        cand_id = rank_data["candidate_id"]
        metrics = rank_data["metrics"]
        
        # Update Candidate with AI summary
        cand = db.query(Candidate).filter(Candidate.id == cand_id).first()
        if cand and not cand.ai_summary:
            cand.ai_summary = rank_data.get("ai_summary", "")
        
        score_obj = CandidateScore(
            candidate_id=cand_id,
            jd_id=job_id,
            similarity_score=metrics["semantic_similarity_score"],
            skill_match_score=metrics["skill_match_score"],
            experience_score=metrics["experience_score"],
            final_score=metrics["final_score"],
            bias_fairness_score=metrics["bias_fairness_score"],
            ranking=rank_data["rank"]
        )
        db.add(score_obj)
        db.commit()
        db.refresh(score_obj)
        response_payload.append(score_obj)
        
    return response_payload

@router.get("/{job_id}/results")
def get_ranked_results(
    job_id: int, 
    skip: int = 0, 
    limit: int = 50, 
    sort_by: str = "final_score",
    db: Session = Depends(get_db)
):
    """Retrieves standard ranking matrix outputs sorted by specific bounds handling pagination cleanly."""
    query = db.query(CandidateScore).filter(CandidateScore.jd_id == job_id)
    
    # Dynamic Sorting Resolution
    if sort_by == "final_score":
        query = query.order_by(CandidateScore.final_score.desc())
    elif sort_by == "bias_score":
        query = query.order_by(CandidateScore.bias_fairness_score.desc())
    else:
        query = query.order_by(CandidateScore.ranking.asc())
        
    results = query.offset(skip).limit(limit).all()
    return results

# ==========================================
# ADVANCED ENHANCEMENTS
# ==========================================

from pydantic import BaseModel
class CommentCreate(BaseModel):
    user_id: int
    note: str

from app.models.comment import Comment

@router.post("/{candidate_id}/comments")
def add_recruiter_note(candidate_id: int, comment_in: CommentCreate, db: Session = Depends(get_db)):
    """Appends explicit Recruiter notes strictly bound against targeted candidates."""
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    comment_obj = Comment(candidate_id=candidate_id, user_id=comment_in.user_id, note=comment_in.note)
    db.add(comment_obj)
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

from fastapi.responses import StreamingResponse
import io
import csv

@router.get("/{job_id}/export")
def export_ranked_candidates_csv(job_id: int, db: Session = Depends(get_db)):
    """Yields an explicit Streaming Bytes .csv formatted mapping without touching hard storage cleanly."""
    scores = db.query(CandidateScore).filter(CandidateScore.jd_id == job_id).order_by(CandidateScore.ranking.asc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Ranking', 'Candidate ID', 'Final Score', 'Skill Match', 'Semantic Sim', 'Bias Score'])
    
    for score in scores:
        writer.writerow([
            score.ranking, 
            score.candidate_id, 
            round(score.final_score, 2), 
            round(score.skill_match_score, 2),
            round(score.similarity_score, 2),
            round(score.bias_fairness_score, 2)
        ])
        
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}_candidates.csv"}
    )
