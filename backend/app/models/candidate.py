from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Candidate(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    resume_file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    # Relationships
    scores = relationship("CandidateScore", back_populates="candidate", cascade="all, delete-orphan")
