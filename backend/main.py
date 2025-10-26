from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth  # , dataset, images, predictions  # Temporarily disabled - missing dependencies
from services.database import engine, Base
from models.user import User
from models.dataset import Dataset
from models.image import Image
from models.annotation import Annotation
from models.prediction import Prediction, SegmentationModel

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
    allow_origins=["http://localhost:3000","http://localhost:5173",
        "http://127.0.0.1:5173","http://127.0.0.1:3000",],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
# app.include_router(dataset.router)  # Temporarily disabled - missing dependencies
# app.include_router(images.router)  # Temporarily disabled - missing dependencies
# app.include_router(predictions.router)  # Temporarily disabled - missing dependencies

@app.get("/")
async def root():
    return {"message": "CAPTCHA Dental AI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
