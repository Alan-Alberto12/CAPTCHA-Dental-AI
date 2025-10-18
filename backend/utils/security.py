from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
from schemas.user import settings
import os
import secrets
import hashlib
import smtplib
from email.message import EmailMessage

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    """Decode a JWT token and return the email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None

def create_reset_token(expires_minutes: int = RESET_TOKEN_EXPIRE_MINUTES):
    # Create a raw reset token for the email link
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(minutes = expires_minutes)

    return raw, token_hash, expires

def hash_reset_token(raw: str) -> str:
    # Hash a raw reset token when created
    return hashlib.sha256(raw.encode()).hexdigest()

def send_reset_email(to_email: str, reset_link: str):
    msg = EmailMessage()
    msg["From"] = settings.MAIL_FROM or "no-reply@captcha.local"
    msg["To"] = to_email
    msg["Subject"] = "Reset your password"
    msg.set_content(f"Click to reset: {reset_link}")

    with smtplib.SMTP(host=settings.SMTP_HOST, port=settings.SMTP_PORT, timeout=10) as smtp:
        # DO NOT call smtp.starttls()
        # DO NOT call smtp.login()
        smtp.send_message(msg)