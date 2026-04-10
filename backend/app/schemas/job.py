from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class JobDescriptionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, description="Job details and requirements")

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)

class JobDescriptionOut(JobDescriptionBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
