from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://captcha_user:captcha_password@localhost:5432/captcha_dental_db")

_ssl = {"sslmode": "require"} if "neon.tech" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=_ssl)
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
