from pydantic import BaseModel, Field
from typing import Optional

class CandidateScoreBase(BaseModel):
    candidate_id: int
    jd_id: int
    similarity_score: float = Field(0.0, ge=0.0, le=100.0)
    skill_match_score: float = Field(0.0, ge=0.0, le=100.0)
    experience_score: float = Field(0.0, ge=0.0, le=100.0)
    final_score: float = Field(0.0, ge=0.0, le=100.0)
    ranking: Optional[int] = None

class CandidateScoreCreate(CandidateScoreBase):
    pass

class CandidateScoreUpdate(BaseModel):
    similarity_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    skill_match_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    experience_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    final_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    ranking: Optional[int] = None

class CandidateScoreOut(CandidateScoreBase):
    id: int

    class Config:
        from_attributes = True
