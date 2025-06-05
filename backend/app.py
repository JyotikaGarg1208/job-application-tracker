from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import Base, engine, get_db
from schemas import UserCreate, UserOut
from models import User
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from auth import oauth2_scheme
from datetime import timedelta
from typing import List
from models import JobApplication
from schemas import JobApplicationCreate, JobApplicationOut
from auth import get_current_user
from fastapi import Path

# 1) Create all tables in database (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2) Health check route
@app.get("/health")
def health_check():
    return {"status": "OK"}

# 3) Registration route
@app.post("/auth/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_pw)

    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 4) Login route
@app.post("/auth/login")
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token; payload: {"sub": user.id}
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 5) Example “get current user” route (to test token)
@app.get("/auth/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

apps_router = FastAPI().router  # we will prefix these routes manually below

@app.post("/apps/", response_model=JobApplicationOut)
def create_app(
    app_in: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create a new JobApplication instance
    db_app = JobApplication(**app_in.dict(), user_id=current_user.id)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/apps/", response_model=List[JobApplicationOut])
def read_apps(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Return all apps for this user, with pagination
    apps = (
        db.query(JobApplication)
        .filter(JobApplication.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return apps

@app.get("/apps/{app_id}", response_model=JobApplicationOut)
def read_app(
    app_id: int = Path(..., title="The ID of the application to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_app = (
        db.query(JobApplication)
        .filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id)
        .first()
    )
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app

@app.put("/apps/{app_id}", response_model=JobApplicationOut)
def update_app(
    app_id: int,
    app_in: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_app = (
        db.query(JobApplication)
        .filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id)
        .first()
    )
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    # Update fields
    for field, value in app_in.dict().items():
        setattr(db_app, field, value)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete("/apps/{app_id}")
def delete_app(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_app = (
        db.query(JobApplication)
        .filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id)
        .first()
    )
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(db_app)
    db.commit()
    return {"detail": "Application deleted"}


