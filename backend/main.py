from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth
from services.database import engine, Base
from models.user import User

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CAPTCHA Dental AI API",
    description="API for dental AI annotation and classification",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "CAPTCHA Dental AI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
