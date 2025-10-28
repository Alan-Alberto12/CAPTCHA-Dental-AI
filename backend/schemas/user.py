from pydantic import BaseModel, EmailStr, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr #emailConformation & resendEmailConfirmation

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

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
    FRONTEND_URL: str = "http://localhost:3000"

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

class EmailConfirmRequest(BaseModel):
    token: str

class ResendConfirmationRequest(BaseModel):
    email: EmailStr

settings = Settings()


class AdminUserRequest(BaseModel):
    """Request schema for admin operations on users (promote/demote)."""
    email: EmailStr
