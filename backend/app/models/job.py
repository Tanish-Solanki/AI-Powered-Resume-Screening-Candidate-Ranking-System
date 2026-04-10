from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.base import Base

class JobDescription(Base):
    __tablename__ = "jobdescription" # explicitly lowercase for ease
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="job_descriptions")
    scores = relationship("CandidateScore", back_populates="job_description", cascade="all, delete-orphan")
