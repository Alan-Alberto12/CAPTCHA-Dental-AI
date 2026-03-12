from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth
from services.database import engine, Base
from models.user import User
from schemas.user import settings
# TODO: Uncomment when these modules are created
# from models.dataset import Dataset
# from models.image import Image
# from models.annotation import Annotation
# from models.prediction import Prediction, SegmentationModel

# Create database tables
#Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CAPTCHA Dental AI API",
    description="API for dental AI annotation and classification",
    version="1.0.0"
)

# Build allowed origins: always include localhost for dev,
# plus whatever FRONTEND_URL is set to (e.g. https://dentag.xyz in production)
_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in _origins:
    _origins.append(settings.FRONTEND_URL.rstrip("/"))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
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
