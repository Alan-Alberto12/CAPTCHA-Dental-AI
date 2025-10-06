from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {"message": "CAPTCHA Dental AI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
