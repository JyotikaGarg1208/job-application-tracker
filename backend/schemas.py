from pydantic import BaseModel, EmailStr

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
