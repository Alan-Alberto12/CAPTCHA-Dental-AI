# FastAPI core
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Database & ORM
from sqlalchemy import Integer
from sqlalchemy.orm import Session; from sqlalchemy.sql import func; from services.database import get_db

# Utilities & stdlib
from datetime import datetime, timedelta, timezone; import secrets, hashlib, random

# Models
from models.user import User, PasswordResetToken, EmailConfirmationToken, Image, Challenge, Annotation, UserStats, UserDataConsent

# Schemas
from schemas.user import UserCreate, UserLogin, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest, EmailConfirmRequest, AdminUserRequest, AnnotationCreate, AnnotationResponse, ChallengeResponse, BulkImageImport, settings, ConsentSubmit, ConsentResponse, ConsentStatusResponse, ConsentHistoryResponse, ConsentHistoryItem

# Security utils
from utils.security import hash_reset_token, send_reset_email, verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, send_confirmation_email


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


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, bg: BackgroundTasks, db: Session = Depends(get_db)):
    """Register a new user and send confirmation email automatically."""
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
        hashed_password=hashed_password,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate and send confirmation token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    confirmation = EmailConfirmationToken(
        user_id=new_user.id,
        token_hash=token_hash,
        expires=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(confirmation)
    db.commit()

    confirm_link = f"{settings.FRONTEND_URL.rstrip('/')}/confirm-email?token={raw_token}"
    bg.add_task(send_confirmation_email, to_email=new_user.email, confirm_link=confirm_link)

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

# emailConfirmation routes
@router.post("/send-confirmation")
def send_confirmation_email_endpoint(
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a new confirmation email to the logged-in user."""
    if current_user.is_verified:
        return {"message": "User already verified."}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    confirmation = EmailConfirmationToken(
        user_id=current_user.id,
        token_hash=token_hash,
        expires=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(confirmation)
    db.commit()

    confirm_link = f"{settings.FRONTEND_URL.rstrip('/')}/confirm-email?token={raw_token}"
    bg.add_task(send_confirmation_email, to_email=current_user.email, confirm_link=confirm_link)

    return {"message": "Confirmation email sent."}


@router.post("/confirm-email")
def confirm_email(payload: EmailConfirmRequest, db: Session = Depends(get_db)):
    """Confirm a user's email via token link."""
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    token_row = db.query(EmailConfirmationToken).filter(EmailConfirmationToken.token_hash == token_hash).first()

    if not token_row or token_row.expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_row.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    user.is_verified = True
    db.add(user)
    db.delete(token_row)
    db.commit()

    return {"message": "Email successfully confirmed!"}


# ADMIN ENDPOINTS
@router.post("/admin/promote", response_model=UserResponse)
def promote_user(
    request: AdminUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # Find the target user by email
    target_user = db.query(User).filter(User.email == request.email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{request.email}' not found"
        )

    # Check if user is already an admin
    if target_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{request.email}' is already an admin"
        )

    # Promote user to admin
    target_user.is_admin = True
    db.commit()
    db.refresh(target_user)

    return target_user

# Demote Admin
@router.post("/admin/demote", response_model=UserResponse)
def demote_user(
    request: AdminUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # Find the user by email
    target_user = db.query(User).filter(User.email == request.email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{request.email}' not found"
        )

    # Prevent self-demotion 
    if target_user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot demote yourself. Ask another admin to demote your account."
        )

    # Check if user is not an admin
    if not target_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{request.email}' is not an admin"
        )

    # Demote user from admin
    target_user.is_admin = False
    db.commit()
    db.refresh(target_user)

    return target_user


@router.get("/challenges/next", response_model=ChallengeResponse)
def get_next_challenge(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    challenge = db.query(Challenge).filter(Challenge.active == True).order_by(func.random()).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="No challenges available")
    return challenge


@router.post("/annotations", response_model=AnnotationResponse, status_code=201)
def submit_annotation(
    payload: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    challenge = db.query(Challenge).filter(Challenge.id == payload.challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    annotation = Annotation(
        user_id=current_user.id,
        challenge_id=payload.challenge_id,
        answer=payload.answer,
        time_spent=payload.time_spent,
        is_correct=None  # to be validated later by AI/admin
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    # Update stats
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id, total_annotations=1)
        db.add(stats)
    else:
        stats.total_annotations += 1
    db.commit()

    return annotation


@router.get("/annotations/me", response_model=list[AnnotationResponse])
def get_my_annotations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    annotations = (
        db.query(Annotation)
        .filter(Annotation.user_id == current_user.id)
        .order_by(Annotation.created_at.desc())
        .all()
    )
    return annotations


@router.post("/admin/import-images", status_code=201)
def import_images(
    payload: BulkImageImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import multiple images and automatically create challenges (admin only)"""

    # Check admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can import images"
        )

    imported_count = 0
    created_challenges = 0

    for image_data in payload.images:
        # Check if image already exists
        existing = db.query(Image).filter(Image.filename == image_data.filename).first()
        if existing:
            continue  # Skip duplicates

        # Create image
        image = Image(
            filename=image_data.filename,
            image_url=image_data.image_url,
            question_type=image_data.question_type,
            question_text=image_data.question_text
        )
        db.add(image)
        db.flush()  # Get the image ID

        # Automatically create a challenge for this image
        challenge = Challenge(
            image_id=image.id,
            active=True
        )
        db.add(challenge)

        imported_count += 1
        created_challenges += 1

    db.commit()

    return {
        "message": "Images imported successfully",
        "images_imported": imported_count,
        "challenges_created": created_challenges
    }

# Data Consent Endpoints

# Grab current user's consent status
@router.get("/consent/status", response_model=ConsentStatusResponse)
def get_consent_status(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return ConsentStatusResponse(
        user_id = current_user.id,
        username = current_user.username,
        has_given_consent = current_user.has_given_data_consent,
        last_update = current_user.last_consent_update,
        has_responded = current_user.has_given_data_consent is not None
    )

# Current Users consent opt in or out
@router.post("/consent/submit", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
def submit_consent(
    payload : ConsentSubmit,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    consent_record = UserDataConsent(
        user_id = current_user.id,
        consent_given = payload.consent_given,
        consented_at = datetime.now(timezone.utc),
        ip_address = None,
        user_agent = None
    )
    db.add(consent_record)

    current_user.has_given_data_consent = payload.consent_given
    current_user.last_consent_update = datetime.now(timezone.utc)
    db.add(current_user)

    db.commit()
    db.refresh(consent_record)

    return consent_record

# Get the complete consent history for the current user
@router.get("/consent/history", response_model=ConsentHistoryResponse)
def get_consent_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = (
        db.query(UserDataConsent)
        .filter(UserDataConsent.user_id == current_user.id)
        .order_by(UserDataConsent.consented_at.desc())
        .all()
    )

    return ConsentHistoryResponse(
        user_id=current_user.id,
        history=[ConsentHistoryItem.model_validate(record) for record in history]
    )

# Get consent statistics (Admin privilege)
@router.get("/admin/consent/summary")
def get_consent_summary(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    opted_in = db.query(User).filter(User.has_given_data_consent == True).count()
    opted_out = db.query(User).filter(User.has_given_data_consent == False).count()
    not_responded = db.query(User).filter(User.has_given_data_consent.is_(None)).count()

    opt_in_percentage = (opted_in / total_users * 100) if total_users > 0 else 0

    return {
        "total_users": total_users,
        "opted_in": opted_in,
        "opted_out": opted_out,
        "not_responded": not_responded,
        "opt_in_percentage": round(opt_in_percentage, 2)
    }

# Grab all users that have opted in (Admin privilege)
@router.get("/admin/consent/users")
def get_users_consent_status(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "has_given_consent": user.has_given_data_consent,
                "last_consent_update": user.last_consent_update,
                "created_at": user.created_at
            }
            for user in users
        ]
    }

# Grab stats for users who have opted in (Admin privilege)
@router.get("/admin/stats/user")
def get_user_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    stats = (
        db.query(
            User.id,
            User.username,
            User.email,
            func.count(Annotation.id).label("total_attempts"),
            func.sum(func.cast(Annotation.is_correct == True, Integer)).label("correct_answers"),
            func.sum(func.cast(Annotation.is_correct == False, Integer)).label("incorrect_answers"),
            func.avg(Annotation.time_spent).label("avg_time_spent")
        )
        .join(Annotation, User.id == Annotation.user_id)
        .filter(User.has_given_data_consent == True)
        .group_by(User.id, User.username, User.email)
        .all()
    )

    results = []
    for stat in stats:
        correct = stat.correct_answers or 0
        incorrect = stat.incorrect_answers or 0
        accuracy = (correct / stat.total_attempts * 100) if stat.total_attempts > 0 else 0
        results.append({
            "user_id": stat.id,
            "username": stat.username,
            "email": stat.email,
            "total_attempts": stat.total_attempts,
            "correct_answers": correct,
            "incorrect_answers": incorrect,
            "accuracy_percentage": round(accuracy, 2),
            "avg_time_spent": round(stat.avg_time_spent, 2) if stat.avg_time_spent else 0
        })
    
     # Get consent breakdown
    total_users = db.query(User).count()
    opted_in = db.query(User).filter(User.has_given_data_consent == True).count()

    return {
        "stats": results,
        "meta": {
            "total_users_in_stats": len(results),
            "total_users": total_users,
            "opted_in_users": opted_in,
            "note": "Only includes users who have explicitly opted in to data usage"
        }
    }