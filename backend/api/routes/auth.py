# FastAPI core
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta, datetime, timezone
import secrets
import hashlib

from services.database import get_db
from models.user import User, PasswordResetToken, EmailConfirmationToken, AnnotationSession, SessionImage, SessionQuestion, Annotation, AnnotationImage, Image, Question, UserStats
from schemas.user import UserCreate, UserLogin, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest, EmailConfirmRequest, UserUpdate, AdminUserRequest, ChallengeResponse, AnnotationResponse, AnnotationCreate, BulkImageImport, BulkQuestionImport, settings
from utils.security import (
    hash_reset_token,
    send_reset_email,
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    send_confirmation_email
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
        first_name=user_data.first_name,
        last_name=user_data.last_name,
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

    confirm_link = f"{settings.FRONTEND_URL.rstrip('/')}/login?token={raw_token}"
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

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox for the confirmation link."
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
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

    confirm_link = f"{settings.FRONTEND_URL.rstrip('/')}/login?token={raw_token}"
    bg.add_task(send_confirmation_email, to_email=current_user.email, confirm_link=confirm_link)

    return {"message": "Confirmation email sent."}


@router.post("/confirm-email")
def confirm_email(payload: EmailConfirmRequest, db: Session = Depends(get_db)):
    """Confirm a user's email via token link."""
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    token_row = db.query(EmailConfirmationToken).filter(EmailConfirmationToken.token_hash == token_hash).first()

    if not token_row or token_row.expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid/expired token")

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


@router.get("/sessions/next")
def get_next_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new annotation session with random images and questions

    Sessions are created with:
    - ALWAYS 4 images
    - Random 1-5 questions
    """
    import random

    # Always use 4 images
    num_images = 4

    # Randomly select 1-5 questions
    num_questions = random.randint(1, 5)

    # Get random images
    images = db.query(Image).order_by(func.random()).limit(num_images).all()
    if len(images) < num_images:
        raise HTTPException(
            status_code=404,
            detail=f"Not enough images available (need {num_images}, found {len(images)})"
        )

    # Get random active questions
    questions = db.query(Question).filter(Question.active == True).order_by(func.random()).limit(num_questions).all()
    if len(questions) < num_questions:
        raise HTTPException(
            status_code=404,
            detail=f"Not enough questions available (need {num_questions}, found {len(questions)})"
        )

    # Create session
    session = AnnotationSession(
        user_id=current_user.id,
    )
    db.add(session)
    db.flush()  # Get session ID without committing

    # Add images to session
    for order, image in enumerate(images, start=1):
        session_image = SessionImage(
            session_id=session.id,
            image_id=image.id,
            image_order=order
        )
        db.add(session_image)

    # Add questions to session
    for order, question in enumerate(questions, start=1):
        session_question = SessionQuestion(
            session_id=session.id,
            question_id=question.id,
            question_order=order
        )
        db.add(session_question)

    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "images": [
            {
                "id": img.id,
                "filename": img.filename,
                "image_url": img.image_url,
                "order": order
            }
            for order, img in enumerate(images, start=1)
        ],
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "order": order
            }
            for order, q in enumerate(questions, start=1)
        ],
        "started_at": session.started_at
    }


@router.post("/annotations", status_code=201)
def submit_annotation(
    payload: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an annotation - user's selected images for a question"""

    # Verify session exists and belongs to current user
    session = db.query(AnnotationSession).filter(AnnotationSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This session doesn't belong to you")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="This session is already completed. You cannot submit more annotations.")

    # Verify question is part of this session
    session_question = db.query(SessionQuestion).filter(
        SessionQuestion.session_id == payload.session_id,
        SessionQuestion.question_id == payload.question_id
    ).first()

    if not session_question:
        raise HTTPException(status_code=400, detail="Question is not part of this session")

    # Check if this question has already been answered in this session
    existing_annotation = db.query(Annotation).filter(
        Annotation.session_id == payload.session_id,
        Annotation.question_id == payload.question_id
    ).first()

    if existing_annotation:
        raise HTTPException(status_code=400, detail="You have already answered this question in this session.")

    # Verify selected images are part of this session
    session_image_ids = db.query(SessionImage.image_id).filter(
        SessionImage.session_id == payload.session_id
    ).all()
    session_image_ids = [img_id[0] for img_id in session_image_ids]

    for image_id in payload.selected_image_ids:
        if image_id not in session_image_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Image {image_id} is not part of this session"
            )

    # Create annotation
    annotation = Annotation(
        session_id=payload.session_id,
        question_id=payload.question_id,
        time_spent=payload.time_spent,
        is_correct=None  # to be validated later by AI/admin
    )
    db.add(annotation)
    db.flush()  # Get annotation ID

    # Store selected images
    for image_id in payload.selected_image_ids:
        annotation_image = AnnotationImage(
            annotation_id=annotation.id,
            image_id=image_id
        )
        db.add(annotation_image)

    db.commit()
    db.refresh(annotation)

    # Check if all questions in this session have been answered
    total_questions = db.query(SessionQuestion).filter(
        SessionQuestion.session_id == payload.session_id
    ).count()

    total_annotations = db.query(Annotation).filter(
        Annotation.session_id == payload.session_id
    ).count()

    # Mark session as completed if all questions answered
    if total_annotations >= total_questions:
        session.is_completed = True
        session.completed_at = datetime.now(timezone.utc)
        db.add(session)

    # Update stats
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id, total_annotations=1)
        db.add(stats)
    else:
        stats.total_annotations += 1
    db.commit()

    return {
        "id": annotation.id,
        "session_id": annotation.session_id,
        "question_id": annotation.question_id,
        "selected_image_ids": payload.selected_image_ids,
        "is_correct": annotation.is_correct,
        "time_spent": annotation.time_spent,
        "created_at": annotation.created_at
    }


@router.get("/annotations/me", response_model=list[AnnotationResponse])
def get_my_annotations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all annotations for the current user's sessions"""
    # Get all sessions for this user
    user_sessions = db.query(AnnotationSession).filter(AnnotationSession.user_id == current_user.id).all()
    session_ids = [s.id for s in user_sessions]

    # Get all annotations from those sessions
    annotations = (
        db.query(Annotation)
        .filter(Annotation.session_id.in_(session_ids))
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
    """Import multiple images (admin only)"""

    # Check admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can import images"
        )

    imported_count = 0

    for image_data in payload.images:
        # Check if image already exists
        existing = db.query(Image).filter(Image.filename == image_data.filename).first()
        if existing:
            continue  # Skip duplicates

        # Create image
        image = Image(
            filename=image_data.filename,
            image_url=image_data.image_url
        )
        db.add(image)
        imported_count += 1

    db.commit()

    return {
        "message": "Images imported successfully",
        "images_imported": imported_count
    }


@router.post("/admin/import-questions", status_code=201)
def import_questions(
    payload: BulkQuestionImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import questions (admin only)"""

    # Check admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can import questions"
        )

    imported_count = 0

    for question_data in payload.questions:
        # Check if question already exists (by text and type)
        existing = db.query(Question).filter(
            Question.question_text == question_data.question_text,
            Question.question_type == question_data.question_type
        ).first()
        if existing:
            continue  # Skip duplicates

        # Create question
        question = Question(
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            active=True
        )
        db.add(question)
        imported_count += 1

    db.commit()

    return {
        "message": "Questions imported successfully",
        "questions_imported": imported_count
    }


@router.put("/editUser", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    # Check if email or username is being changed and already exists
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name

    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name

    # Update password if provided
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)

    return current_user
