from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.RECRUITER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserOut(UserInDB):
    pass
