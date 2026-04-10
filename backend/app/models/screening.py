from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class CandidateScore(Base):
    __tablename__ = "candidatescore"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate.id"), nullable=False, index=True)
    jd_id = Column(Integer, ForeignKey("jobdescription.id"), nullable=False, index=True)
    
    similarity_score = Column(Float, nullable=False, default=0.0)
    skill_match_score = Column(Float, nullable=False, default=0.0)
    experience_score = Column(Float, nullable=False, default=0.0)
    final_score = Column(Float, nullable=False, default=0.0)
    bias_fairness_score = Column(Float, nullable=False, default=100.0)
    ranking = Column(Integer, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="scores")
    job_description = relationship("JobDescription", back_populates="scores")
