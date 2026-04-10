import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateOut
from app.utils.resume_parser import parse_resume
from app.ml.skill_extractor import process_and_extract_entities
from app.core.config import settings

router = APIRouter(prefix="/resumes", tags=["resume parsing"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=List[CandidateOut], status_code=status.HTTP_201_CREATED)
async def upload_resumes(
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    """
    Accepts multiple resume files (PDF, DOCX).
    Saves to disk, parses text, extracts entities, and creates Candidate objects.
    """
    created_candidates = []
    
    for file in files:
        # Validate format
        file_ext = file.filename.lower().split('.')[-1]
        if file_ext not in ["pdf", "docx", "txt"]:
            continue # Skip invalid files
            
        # Save file to disk securely
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Run NLP parsing pipeline
        parsed_data = parse_resume(file_path)
        if not parsed_data:
            # Handle failed parsings
            continue
            
        # Extract skills (Not directly saved to Candidate table directly here, but could be)
        entities = process_and_extract_entities(parsed_data)
        
        # Determine candidate name (fallback to filename if extraction fails to pinpoint NAME entity)
        # Advanced implementations would use Spacy PER entities here.
        candidate_name = file.filename.replace(f".{file_ext}", "")
        
        # Create DB record
        candidate_obj = Candidate(
            name=candidate_name,
            # Email/Phone could also be ripped via Regex inside parser in production
            email=None, 
            phone=None,
            resume_file_path=file_path,
            extracted_text=parsed_data.get("raw_text", "")
        )
        db.add(candidate_obj)
        db.commit()
        db.refresh(candidate_obj)
        created_candidates.append(candidate_obj)
        
    return created_candidates
