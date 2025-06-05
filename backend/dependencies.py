from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1) DATABASE_URL: where our DB lives. Default to SQLite for local testing.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# 2) Create a SQLAlchemy engine
#    - connect_args={"check_same_thread": False} is SQLite‐specific
#    - On production (Postgres), DATABASE_URL will be something like "postgresql://..."
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3) Create a sessionmaker: each request gets its own DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4) Base class for our models (tables)
Base = declarative_base()

# 5) Dependency function for FastAPI
def get_db():
    """
    When a request is made, yields a DB session.
    After request ends, closes the session automatically.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
