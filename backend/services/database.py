from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__).info(f"Connecting to DB host: {DATABASE_URL.split('@')[-1].split('/')[0]}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    Use this in route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
