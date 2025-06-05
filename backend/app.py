from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import Base, engine, get_db
from schemas import UserCreate, UserOut
from models import User
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from auth import oauth2_scheme
from datetime import timedelta

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


