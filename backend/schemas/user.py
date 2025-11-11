from pydantic import BaseModel, EmailStr, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
from typing import Optional

# user schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# stats schemas
class UserStatsResponse(BaseModel):
    total_points: int
    total_annotations: int
    accuracy_rate: float
    daily_streak: int

    class Config:
        from_attributes = True


class UserResponse(UserBase): 
    id: int
    challenge_id: int
    answer: str
    is_correct: bool | None
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    stats: Optional[UserStatsResponse] = None

    class Config:
        from_attributes = True

#auth / token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email : EmailStr    

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)   # raw token from the email link
    new_password: str = Field(..., min_length=8)
    
class Settings(BaseSettings):
    # --- app / db ---
    DATABASE_URL: str = "postgresql://captcha_user:captcha_password@db:5432/captcha_dental_db"
    FRONTEND_URL: str = "http://localhost:5173"

    # --- auth/JWT ---
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- email (MailHog in dev) ---
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    MAIL_FROM: str = "no-reply@captcha.local"

    # tell pydantic-settings to read .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


#email confirmation schemas
class EmailConfirmRequest(BaseModel):
    token: str

class ResendConfirmationRequest(BaseModel):
    email: EmailStr

settings = Settings()

#admin user schema
class AdminUserRequest(BaseModel):
    """Request schema for admin operations on users (promote/demote)."""
    email: EmailStr


# annotation, image, question, session schemas
class ImageResponse(BaseModel):
    id: int
    filename: str
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: int
    user_id: int
    is_completed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnnotationCreate(BaseModel):
    session_id: int
    question_id: int
    selected_image_ids: list[int]  # List of image IDs the user selected
    time_spent: Optional[float] = None


class ImageImport(BaseModel):
    """Schema for importing a single image"""
    filename: str
    image_url: str


class BulkImageImport(BaseModel):
    """Schema for bulk importing images"""
    images: list[ImageImport]


class QuestionImport(BaseModel):
    """Schema for importing a single question"""
    question_text: str
    question_type: str


class BulkQuestionImport(BaseModel):
    """Schema for bulk importing questions"""
    questions: list[QuestionImport]


class AnnotationResponse(BaseModel):
    id: int
    session_id: int
    question_id: int
    selected_image_ids: list[int]  # Which images user selected
    is_correct: Optional[bool] = None
    time_spent: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Kept for backwards compatibility (will be removed later)
class ChallengeResponse(BaseModel):
    id: int
    image: ImageResponse
    created_at: datetime

    class Config:
        from_attributes = True
