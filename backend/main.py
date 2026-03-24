from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, ml, leaderboard
from services.database import engine, Base
from models.user import User
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CAPTCHA Dental AI API",
    description="API for dental AI annotation and classification",
    version="1.0.0"
)

# CORS configuration
_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url:
    _origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(ml.router)
app.include_router(leaderboard.router)

@app.get("/")
async def root():
    return {"message": "CAPTCHA Dental AI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
