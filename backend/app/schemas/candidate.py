from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CandidateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)

class CandidateCreate(CandidateBase):
    resume_file_path: str = Field(..., max_length=500)
    extracted_text: Optional[str] = None

class CandidateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    resume_file_path: Optional[str] = Field(None, max_length=500)
    extracted_text: Optional[str] = None

class CandidateOut(CandidateBase):
    id: int
    resume_file_path: str
    
    # We might not want to return the raw extracted_text on every list query
    # to save bandwidth, but we can include it in specific Detail schema
    
    class Config:
        from_attributes = True

class CandidateDetail(CandidateOut):
    extracted_text: Optional[str] = None
