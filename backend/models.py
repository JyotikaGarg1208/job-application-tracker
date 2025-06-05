from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from dependencies import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship so we can do user.applications
    applications = relationship("JobApplication", back_populates="user")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, index=True, nullable=False)
    company = Column(String, index=True, nullable=False)
    date_applied = Column(Date, nullable=False)
    status = Column(String, default="Applied", nullable=False)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    next_steps = Column(Date, nullable=True)

    # Relationship back to User
    user = relationship("User", back_populates="applications")

