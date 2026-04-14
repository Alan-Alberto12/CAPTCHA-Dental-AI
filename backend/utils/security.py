from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
from schemas.user import settings
import os
import secrets
import hashlib
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
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

def _send_email(msg: EmailMessage) -> None:
    """Send an email via SMTP. Uses STARTTLS + login when credentials are configured."""
    try:
        with smtplib.SMTP(host=settings.SMTP_HOST, port=settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        logger.error("Failed to send email to %s: %s", msg["To"], e)
        raise

def send_reset_email(to_email: str, reset_link: str):
    msg = EmailMessage()
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Reset your CAPTCHA Dental AI password"
    msg.set_content(
        f"You requested a password reset for your CAPTCHA Dental AI account.\n\n"
        f"Click the link below to reset your password (expires in 30 minutes):\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, you can safely ignore this email."
    )
    msg.add_alternative(f"""
    <html><body style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;">
      <h2>Reset your password</h2>
      <p>You requested a password reset for your CAPTCHA Dental AI account.</p>
      <p>
        <a href="{reset_link}" style="display:inline-block;padding:12px 24px;background:#6c5ce7;color:#fff;text-decoration:none;border-radius:6px;font-weight:bold;">
          Reset Password
        </a>
      </p>
      <p style="color:#888;font-size:13px;">This link expires in 30 minutes. If you did not request this, you can safely ignore this email.</p>
    </body></html>
    """, subtype="html")
    _send_email(msg)

def send_confirmation_email(to_email: str, confirm_link: str):
    """Send email confirmation message with a verification link."""
    msg = EmailMessage()
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Confirm your CAPTCHA Dental AI account"
    msg.set_content(
        f"Welcome to CAPTCHA Dental AI!\n\n"
        f"Please confirm your email address by clicking the link below (expires in 1 hour):\n\n"
        f"{confirm_link}\n\n"
        f"If you did not create an account, you can safely ignore this email."
    )
    msg.add_alternative(f"""
    <html><body style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;">
      <h2>Welcome to CAPTCHA Dental AI!</h2>
      <p>Please confirm your email address to activate your account.</p>
      <p>
        <a href="{confirm_link}" style="display:inline-block;padding:12px 24px;background:#6c5ce7;color:#fff;text-decoration:none;border-radius:6px;font-weight:bold;">
          Confirm Email
        </a>
      </p>
      <p style="color:#888;font-size:13px;">This link expires in 1 hour. If you did not create an account, you can safely ignore this email.</p>
    </body></html>
    """, subtype="html")
    _send_email(msg)
