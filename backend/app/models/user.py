from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.database.base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.RECRUITER, nullable=False)

    # Relationships
    job_descriptions = relationship("JobDescription", back_populates="creator")
