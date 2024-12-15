from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Retrieve the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError(
        "The DATABASE_URL environment variable is not set. "
        "Please set it to a valid database connection string. "
        "For local development, you can use 'sqlite:///example.db'."
    )

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a new database session for each use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
