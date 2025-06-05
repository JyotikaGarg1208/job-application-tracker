from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# 1) Input data for registration/login
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 2) Output model (what we return to client)
class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class JobApplicationBase(BaseModel):
    role: str
    company: str
    date_applied: date
    status: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    next_steps: Optional[date] = None

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplicationOut(JobApplicationBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
