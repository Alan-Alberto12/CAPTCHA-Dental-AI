from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
import secrets
import hashlib

from services.database import get_db
from models.user import PasswordResetToken, User
from schemas.user import UserCreate, UserLogin, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest, settings
from utils.security import (
    hash_reset_token,
    send_reset_email,
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token."""
    # Find user by email or username (using username field from OAuth2 form)
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

# ----- FORGOT PASSWORD -----
@router.post("/forgot-password")
def forgot_password(payload : ForgotPasswordRequest, bg : BackgroundTasks, db : Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if user:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        reset = PasswordResetToken(user_id = user.id, token_hash = token_hash, expires = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
        db.add(reset)
        db.commit()

        # Password reset link
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw_token}"
        bg.add_task(send_reset_email, to_email=user.email, reset_link=reset_link)

        return {"message": "If that email exists, a password reset link has been sent."}
    
@router.post("/reset-password", status_code = 200)
def reset_password(payload : ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token)
    token_row = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()

    if not token_row:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid or expired token")
    
    # If token is expired
    if token_row.expires < datetime.now(timezone.utc):
        db.delete(token_row) #Delete it
        db.commit()

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid or expired token")
    
    # Update user password
    user = db.query(User).filter(User.id == token_row.user_id).first()

    if not user:
        db.delete(token_row)
        db.commit()

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid or expired token")

    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user) 

    # Delete token since it is a one time use
    db.delete(token_row)
    db.commit()

    return {"message": "Password has been successfully reset"}

