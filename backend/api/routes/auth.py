# FastAPI core
from fileinput import filename

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import timedelta, datetime, timezone
import secrets
import hashlib
import zipfile
import io
import random

from services.database import get_db
from services.s3_service import s3_service
from models.user import (
    Prediction,
    User,
    PasswordResetToken,
    EmailConfirmationToken,
    AnnotationSession,
    SessionImage,
    SessionQuestion,
    Annotation,
    AnnotationImage,
    Image,
    Question,
    UserStats,
    Prediction,
    PointTransaction,
)
from schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    EmailConfirmRequest,
    UserUpdate,
    AdminUserRequest,
    ChallengeResponse,
    AnnotationResponse,
    AnnotationCreate,
    BulkImageImport,
    BulkQuestionImport,
    SessionTitleUpdate,
    settings,
    AdminUserOverview,
    AdminAllUsersOverview,
)
from utils.security import (
    hash_reset_token,
    send_reset_email,
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    send_confirmation_email,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
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
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

@router.get("/admin/users")
def list_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Return all users with their stats. Admin only."""
    users = db.query(User).order_by(User.created_at.desc()).all()
 
    result = []
    for user in users:
        # Pull UserStats row (may not exist for brand-new users)
        stats = db.query(UserStats).filter(UserStats.user_id == user.id).first()
 
        # Compute total time from completed annotation sessions
        # time_spent is stored in seconds on each Annotation row
        total_seconds = (
            db.query(func.sum(Annotation.time_spent))
            .join(AnnotationSession, Annotation.session_id == AnnotationSession.id)
            .filter(AnnotationSession.user_id == user.id)
            .scalar()
        ) or 0
 
        total_minutes = round(total_seconds / 60)
 
        # Average session time across completed sessions
        completed_sessions = (
            db.query(AnnotationSession)
            .filter(
                AnnotationSession.user_id == user.id,
                AnnotationSession.is_completed == True
            )
            .all()
        )
 
        avg_session_minutes = 0
        if completed_sessions:
            session_times = []
            for s in completed_sessions:
                secs = (
                    db.query(func.sum(Annotation.time_spent))
                    .filter(Annotation.session_id == s.id)
                    .scalar()
                ) or 0
                session_times.append(secs / 60)
            avg_session_minutes = round(sum(session_times) / len(session_times))
 
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "stats": {
                "total_annotations": stats.total_annotations if stats else 0,
                "total_time_minutes": total_minutes,
                "avg_session_time_minutes": avg_session_minutes,
            },
        })
 
    return result

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, bg: BackgroundTasks, db: Session = Depends(get_db)):
    """Register a new user and send confirmation email automatically."""
    existing_user = db.query(User).filter(
        (func.lower(User.email) == user_data.email.lower()) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email.lower(),
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    confirmation = EmailConfirmationToken(
        user_id=new_user.id,
        token_hash=token_hash,
        expires=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(confirmation)
    db.commit()

    confirm_link = f"{settings.FRONTEND_URL.rstrip('/')}/login?token={raw_token}"
    bg.add_task(send_confirmation_email, to_email=new_user.email, confirm_link=confirm_link)

    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    login_input = form_data.username
    if "@" in login_input:
        user = db.query(User).filter(func.lower(User.email) == login_input.lower()).first()
    else:
        user = db.query(User).filter(User.username == login_input).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox for the confirmation link.",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
    return current_user


# ----- FORGOT PASSWORD -----
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if user:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        reset = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        db.add(reset)
        db.commit()

        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw_token}"
        bg.add_task(send_reset_email, to_email=user.email, reset_link=reset_link)

    # always return the same message — don't reveal whether the email exists
    return {"message": "If that email exists, a password reset link has been sent."}
    

@router.post("/reset-password", status_code=200)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token)
    token_row = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()

    if not token_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    if token_row.expires < datetime.now(timezone.utc):
        db.delete(token_row)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_row.user_id).first()

    if not user:
        db.delete(token_row)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)
    db.delete(token_row)
    db.commit()

    return {"message": "Password has been successfully reset"}


# emailConfirmation routes
@router.post("/send-confirmation")
def send_confirmation_email_endpoint(
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a new confirmation email to the logged-in user."""
    if current_user.is_verified:
        return {"message": "User already verified."}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    confirmation = EmailConfirmationToken(
        user_id=current_user.id,
        token_hash=token_hash,
        expires=datetime.now(timezone.utc) + timedelta(hours=1),
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

    # If token was already used and user is verified, treat as success (handles Microsoft scanner pre-fetching the link)
    if token_row and token_row.used:
        user = db.query(User).filter(User.id == token_row.user_id).first()
        if user and user.is_verified:
            return {"message": "Email successfully confirmed!"}

    if not token_row or token_row.expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid/expired token")

    user = db.query(User).filter(User.id == token_row.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    user.is_verified = True
    db.add(user)
    token_row.used = True
    db.add(token_row)
    db.commit()

    return {"message": "Email successfully confirmed!"}


# ADMIN ENDPOINTS
@router.post("/admin/promote", response_model=UserResponse)
def promote_user(
    request: AdminUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    target_user = db.query(User).filter(User.email == request.email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{request.email}' not found",
        )

    if target_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{request.email}' is already an admin",
        )

    target_user.is_admin = True
    db.commit()
    db.refresh(target_user)
    return target_user


@router.post("/admin/demote", response_model=UserResponse)
def demote_user(
    request: AdminUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    target_user = db.query(User).filter(User.email == request.email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{request.email}' not found",
        )

    if target_user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot demote yourself. Ask another admin to demote your account.",
        )

    if not target_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{request.email}' is not an admin",
        )

    target_user.is_admin = False
    db.commit()
    db.refresh(target_user)
    return target_user


@router.get("/sessions/current")
def get_current_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the user's current incomplete session, or return null if none exists"""
    session = (
        db.query(AnnotationSession)
        .filter(
            AnnotationSession.user_id == current_user.id,
            AnnotationSession.is_completed == False,
        )
        .order_by(AnnotationSession.started_at.desc())
        .first()
    )

    if not session:
        return None

    session_questions = (
        db.query(SessionQuestion)
        .filter(SessionQuestion.session_id == session.id)
        .order_by(SessionQuestion.question_order)
        .all()
    )

    questions = []
    for sq in session_questions:
        question = db.query(Question).filter(Question.id == sq.question_id).first()
        if question:
            images_per_q = (
                db.query(SessionImage)
                .filter(SessionImage.session_id == session.id, SessionImage.question_id == sq.question_id)
                .order_by(SessionImage.image_order)
                .all()
            )
            images = []
            for si in images_per_q:
                image = db.query(Image).filter(Image.id == si.image_id).first()
                if image:
                    images.append ({
                        "id": image.id,
                        "filename": image.filename,
                        "image_url": s3_service.generate_presigned_url(image.image_url, expiration=10) or image.image_url,
                        "order": si.image_order,
                    })
            questions.append({
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "order": sq.question_order,
                "images": images,
            })

    answered_annotations = db.query(Annotation.question_id).filter(Annotation.session_id == session.id).all()
    answered_question_ids = [a[0] for a in answered_annotations]

    completed_count = db.query(AnnotationSession).filter(
        AnnotationSession.user_id == current_user.id,
        AnnotationSession.is_completed == True
    ).count()
    session_number = completed_count + 1

    return {
        "session_id": session.id,
        "session_number": session_number,
        "images": [],  # images are now nested under each question, so we can return an empty array to simplify frontend handling -DH
        "questions": questions,
        "answered_question_ids": answered_question_ids,
        "started_at": session.started_at,
    }

@router.get("/sessions/completed")
def get_completed_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all completed sessions for the current user to display on Dashboard"""
    
    sessions = db.query(AnnotationSession).filter(
        AnnotationSession.user_id == current_user.id,
        AnnotationSession.is_completed == True
    ).order_by(AnnotationSession.completed_at.desc()).all()

    total = len(sessions)
    result = []
    for index, session in enumerate(sessions):

        session_number = total - index

        # Get question count for this session
        question_count = db.query(SessionQuestion).filter(
            SessionQuestion.session_id == session.id
        ).count()

        # get the first image for this session (thumbnail on Dashboard tab)
        session_first_image = db.query(SessionImage).filter(
            SessionImage.session_id == session.id
        ).order_by(SessionImage.image_order).first()

        thumbnail_url = None
        if session_first_image:
            image = db.query(Image).filter(Image.id == session_first_image.image_id).first()
            if image:
                thumbnail_url = s3_service.generate_presigned_url(image.image_url, expiration=10)

        points_earned = db.query(func.sum(PointTransaction.points)).filter(
            PointTransaction.session_id == session.id
        ).scalar() or 0

        result.append({
            "session_id": session.id,
            "title": session.title,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "question_count": question_count,
            "thumbnail_url": thumbnail_url,
            "session_number": session_number,
            "points_earned": points_earned,
        })

    return result

@router.get("/sessions/{session_id}/overview")
def get_session_overview (
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # get overview of a session: submitted responses per question
    completed_session = db.query(AnnotationSession).filter(AnnotationSession.id == session_id).first()

    # verify the edge cases that could break the app
    if not completed_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if completed_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This session doesn't belong to you")

    if not completed_session.is_completed:
        raise HTTPException(status_code=400, detail="Session is not completed")

    # get the questions in order with per-question images
    completed_session_questions = (
        db.query(SessionQuestion).filter(SessionQuestion.session_id == completed_session.id)
        .order_by(SessionQuestion.question_order).all()
    )
    questions = []
    for sq in completed_session_questions:
        question = db.query(Question).filter(Question.id == sq.question_id).first()
        if question:
            images_per_q = (
                db.query(SessionImage)
                .filter(SessionImage.session_id == completed_session.id, SessionImage.question_id == sq.question_id)
                .order_by(SessionImage.image_order).all()
            )
            images = []
            for si in images_per_q:
                image = db.query(Image).filter(Image.id == si.image_id).first()
                if image:
                    images.append({
                        "id": image.id,
                        "filename": image.filename,
                        "image_url": s3_service.generate_presigned_url(image.image_url, expiration=10) or image.image_url,
                        "order": si.image_order,
                    })
            questions.append({
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "order": sq.question_order,
                "images": images,
            })

    # arrange image IDs per question
    selected_images_per_question = {}
    for sq in completed_session_questions:
        annotation = db.query(Annotation).filter(Annotation.session_id == completed_session.id, Annotation.question_id == sq.question_id).first()
        if annotation:
            selected_ids = [
                ai.image_id for ai in
                db.query(AnnotationImage).filter(AnnotationImage.annotation_id == annotation.id).all()
            ]
            selected_images_per_question[sq.question_id] = selected_ids
        else:
            selected_images_per_question[sq.question_id] = []

    return {
        "session_id": completed_session.id,
        "title": completed_session.title,
        "completed_at": completed_session.completed_at,
        "questions": questions,
        "selected_images_per_question": selected_images_per_question,
    }
    


@router.get("/sessions/next")
def get_next_session(
    force_new: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # resume existing session if one is in progress
    if not force_new:
        existing = get_current_session(db=db, current_user=current_user)
        if existing and existing.get("questions"):
            return {**existing, "resumed": True}

    num_images_per_question = 4
    num_questions = 3

    questions = (
        db.query(Question)
        .filter(Question.active == True)
        .order_by(func.random())
        .limit(num_questions)
        .all()
    )
    if len(questions) < num_questions:
        raise HTTPException(status_code=404, detail=f"Not enough questions available (need {num_questions}, found {len(questions)})")

    session = AnnotationSession(user_id=current_user.id)
    db.add(session)
    db.flush()

    # Select all images needed for the session at once to avoid duplicates across questions
    total_images_needed = num_questions * num_images_per_question
    all_session_images = db.query(Image).order_by(func.random()).limit(total_images_needed).all()
    if len(all_session_images) < total_images_needed:
        raise HTTPException(status_code=404, detail=f"Not enough images available (need {total_images_needed}, found {len(all_session_images)})")

    images_per_q_map = {}
    for order, question in enumerate(questions, start=1):
        db.add(SessionQuestion(session_id=session.id, question_id=question.id, question_order=order))
        start = (order - 1) * num_images_per_question
        images_per_q = all_session_images[start:start + num_images_per_question]
        images_per_q_map[question.id] = images_per_q
        for image_order, image in enumerate(images_per_q, start=1):
            db.add(SessionImage(session_id=session.id, image_id=image.id, question_id=question.id, image_order=image_order))

    db.commit()
    db.refresh(session)

    completed_count = db.query(AnnotationSession).filter(
        AnnotationSession.user_id == current_user.id,
        AnnotationSession.is_completed == True
    ).count()
    session_number = completed_count + 1

    return {
        "session_id": session.id,
        "session_number": session_number,
        "images": [],
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "order": order,
                "images": [
                    {
                        "id": img.id,
                        "filename": img.filename,
                        "image_url": s3_service.generate_presigned_url(img.image_url, expiration=10) or img.image_url,
                        "order": img_order,
                    }
                    for img_order, img in enumerate(images_per_q_map[q.id], start=1)
                ],
            }
            for order, q in enumerate(questions, start=1)
        ],
        "answered_question_ids": [],
        "started_at": session.started_at,
        "resumed": False,
    }


@router.post("/annotations", status_code=201)
def submit_annotation(payload: AnnotationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Submit an annotation - user's selected images for a question"""
    session = db.query(AnnotationSession).filter(AnnotationSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This session doesn't belong to you")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="This session is already completed. You cannot submit more annotations.")

    session_question = db.query(SessionQuestion).filter(
        SessionQuestion.session_id == payload.session_id,
        SessionQuestion.question_id == payload.question_id
    ).first()
    if not session_question:
        raise HTTPException(status_code=400, detail="Question is not part of this session")

    existing_annotation = db.query(Annotation).filter(
        Annotation.session_id == payload.session_id,
        Annotation.question_id == payload.question_id
    ).first()
    if existing_annotation:
        raise HTTPException(status_code=400, detail="You have already answered this question in this session.")

    session_image_ids = db.query(SessionImage.image_id).filter(SessionImage.session_id == payload.session_id).all()
    session_image_ids = [img_id[0] for img_id in session_image_ids]

    for image_id in payload.selected_image_ids:
        if image_id not in session_image_ids:
            raise HTTPException(status_code=400, detail=f"Image {image_id} is not part of this session")

    annotation = Annotation(
        session_id=payload.session_id,
        question_id=payload.question_id,
        time_spent=payload.time_spent,
        is_correct=None
    )
    db.add(annotation)
    db.flush()

    for image_id in payload.selected_image_ids:
        db.add(AnnotationImage(annotation_id=annotation.id, image_id=image_id))

    db.commit()
    db.refresh(annotation)

    total_questions = db.query(SessionQuestion).filter(SessionQuestion.session_id == payload.session_id).count()
    total_annotations = db.query(Annotation).filter(Annotation.session_id == payload.session_id).count()

    if total_annotations >= total_questions:
        session.is_completed = True
        session.completed_at = datetime.now(timezone.utc)
        db.add(session)

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
        "created_at": annotation.created_at,
    }


@router.get("/annotations/me", response_model=list[AnnotationResponse])
def get_my_annotations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all annotations for the current user's sessions"""
    user_sessions = db.query(AnnotationSession).filter(AnnotationSession.user_id == current_user.id).all()
    session_ids = [s.id for s in user_sessions]

    annotations = (
        db.query(Annotation)
        .filter(Annotation.session_id.in_(session_ids))
        .order_by(Annotation.created_at.desc())
        .all()
    )
    return annotations


@router.post("/admin/import-images-url", status_code=201)
def import_images_url(payload: BulkImageImport, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Import multiple images from URLs (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can import images")
@router.patch("/sessions/{session_id}/title")
def update_session_title(
    session_id: int,
    payload: SessionTitleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the title of a completed session"""
    session = db.query(AnnotationSession).filter(AnnotationSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This session doesn't belong to you")

    if not session.is_completed:
        raise HTTPException(status_code=400, detail="Can only title completed sessions")

    session.title = payload.title
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "title": session.title,
        "message": "Session title updated successfully"
    }


@router.post("/admin/import-images-url", status_code=201)
def import_images_url(
    payload: BulkImageImport,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    imported_count = 0
    for image_data in payload.images:
        existing = db.query(Image).filter(Image.filename == image_data.filename).first()
        if existing:
            continue

        db.add(Image(filename=image_data.filename, image_url=image_data.image_url))
        imported_count += 1

    db.commit()
    return {"message": "Images imported successfully", "images_imported": imported_count}


@router.post("/admin/import-images-file", status_code=201)
async def import_images_file(
    files: list[UploadFile] = File(...),
    folder_name: str = "image_upload",
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload single or multiple image files to S3 (admin only).

    Images predicted as needs_expert_review are also saved to the DB.
    Images predicted as does_not_need_expert_review are stored in S3 only.
    If no trained model is available, all images are saved to the DB.
    """
    try:
        from ml.predict import PredictionService
        _ml_available = True
    except Exception:
        PredictionService = None
        _ml_available = False

    ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/avif"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per image

    if _ml_available:
        prediction_service = PredictionService.get_instance()
        if prediction_service.model is None:
            prediction_service.load_model()
        model_available = prediction_service.model is not None
    else:
        prediction_service = None
        model_available = False

    results = []
    failed = []

    def upload_image(filename: str, file_data: bytes, content_type: str):
        if len(file_data) > MAX_FILE_SIZE:
            return None, {"filename": filename, "error": f"File too large ({len(file_data)} bytes). Max: {MAX_FILE_SIZE}"}

        # Check DB first — skip S3 upload entirely if already saved
        existing = db.query(Image).filter(Image.filename == filename).first()
        if existing:
            existing_prediction = db.query(Prediction).filter(Prediction.image_id == existing.id).order_by(Prediction.id.desc()).first()
            return {"filename": filename, "image_url": existing.image_url, "label": existing_prediction.predicted_label if existing_prediction else None, "confidence": existing_prediction.confidence if existing_prediction else None, "saved_to_db": True, "already_existed": True}, None


        s3_url = s3_service.upload_file(
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            folder=folder_name
        )
        if not s3_url:
            return None, {"filename": filename, "error": "Failed to upload to S3"}

        if not model_available:
            return None, {"filename": filename, "error": "No trained model available. Cannot classify image."}

        label = "needs_expert_review"
        confidence = None
        try:
            pred = prediction_service.predict(file_data)
            label = pred["label"]
            confidence = pred["confidence"]
        except Exception as e:
            return None, {"filename": filename, "error": f"Prediction failed: {str(e)}"}

        saved_to_db = False
        if label == "needs_expert_review":
            db.add(Image(filename=filename, image_url=s3_url))
            db.commit()
            saved_to_db = True
            # Save prediction to DB
            image_prediction = db.query(Image).filter(Image.filename == filename).first()
            if image_prediction and confidence is not None:
                db.add(Prediction(
                    image_id=image_prediction.id,
                    model_name=prediction_service.arch,
                    predicted_label=label,
                    confidence=confidence,
                    model_version="latest",
                ))
                db.commit()

        return {"filename": filename, "image_url": s3_url, "label": label, "confidence": confidence, "saved_to_db": saved_to_db, "already_existed": False}, None

    for file in files:
        try:
            if file.content_type not in ALLOWED_TYPES:
                failed.append({"filename": file.filename, "error": f"Invalid file type: {file.content_type}. Allowed: JPEG, PNG, WEBP"})
                continue

            file_data = await file.read()

            if len(file_data) > MAX_FILE_SIZE:
                failed.append({"filename": file.filename, "error": f"File too large: {len(file_data)} bytes. Max: {MAX_FILE_SIZE} bytes"})
                continue

            result, error = upload_image(file.filename, file_data, file.content_type)
            if error:
                failed.append(error)
            else:
                results.append(result)

        except Exception as e:
            failed.append({"filename": file.filename, "error": str(e)})
            file_data = await file.read()

            if file.filename.lower().endswith(".zip") or file.content_type in ("application/zip", "application/x-zip-compressed"):
                try:
                    with zipfile.ZipFile(io.BytesIO(file_data)) as zf:
                        for entry in zf.infolist():
                            if entry.is_dir():
                                continue
                            inner_name = entry.filename.split("/")[-1]
                            if inner_name.startswith("._") or inner_name.startswith("."):
                                continue
                            ext = "." + inner_name.rsplit(".", 1)[-1].lower() if "." in inner_name else ""
                            if ext not in ALLOWED_EXTENSIONS:
                                continue
                            inner_data = zf.read(entry)
                            content_type = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext[1:]}"
                            result, error = upload_image(inner_name, inner_data, content_type)
                            if error:
                                failed.append(error)
                            else:
                                results.append(result)
                except zipfile.BadZipFile:
                    failed.append({"filename": file.filename, "error": "Invalid or corrupted ZIP file"})
                continue

            if file.content_type not in ALLOWED_TYPES:
                failed.append({"filename": file.filename, "error": f"Invalid file type: {file.content_type}. Allowed: JPEG, PNG, WEBP, ZIP"})
                continue

            result, error = upload_image(file.filename, file_data, file.content_type)
            if error:
                failed.append(error)
            else:
                results.append(result)

        except Exception as e:
            failed.append({"filename": file.filename, "error": str(e)})

    saved_to_db_count = sum(1 for r in results if r.get("saved_to_db"))
    already_existed_count = sum(1 for r in results if r.get("already_existed"))

    return {
        "uploaded": len(results),
        "already_existed": already_existed_count,
        "saved_to_db": saved_to_db_count,
        "s3_only": len(results) - saved_to_db_count,
        "failed": len(failed),
        "folder": folder_name,
        "results": results,
        "failures": failed,
    }


@router.post("/admin/import-questions", status_code=201)
def import_questions(
    payload: BulkQuestionImport,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    imported_count = 0
    for question_data in payload.questions:
        existing = db.query(Question).filter(
            Question.question_text == question_data.question_text,
            Question.question_type == question_data.question_type
        ).first()
        if existing:
            continue

        db.add(Question(question_text=question_data.question_text, question_type=question_data.question_type, active=True))
        imported_count += 1

    db.commit()
    return {"message": "Questions imported successfully", "questions_imported": imported_count}


@router.put("/editUser", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if email or username is being changed and already exists
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        current_user.email = user_update.email

    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        current_user.username = user_update.username

    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name

    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name

    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user


# Admin: All Users Submission Overview  ✅ FIXED (uses case(), not func.case())
@router.get("/admin/users/submissions-overview", response_model=AdminAllUsersOverview)
def all_users_submission_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Admin: aggregated submission stats for all users."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can view this data")

    sessions_sq = (
        db.query(
            AnnotationSession.user_id.label("user_id"),
            func.count(AnnotationSession.id).label("total_sessions"),
            func.coalesce(
                func.sum(case((AnnotationSession.is_completed == True, 1), else_=0)),
                0
            ).label("completed_sessions"),
            func.max(AnnotationSession.started_at).label("last_session_at"),
        )
        .group_by(AnnotationSession.user_id)
        .subquery()
    )

    annotations_sq = (
        db.query(
            AnnotationSession.user_id.label("user_id"),
            func.count(Annotation.id).label("total_annotations"),
        )
        .join(AnnotationSession, Annotation.session_id == AnnotationSession.id)
        .group_by(AnnotationSession.user_id)
        .subquery()
    )

    rows = (
        db.query(
            User.id.label("user_id"),
            User.email.label("email"),
            User.username.label("username"),
            User.is_admin.label("is_admin"),
            User.is_active.label("is_active"),
            User.is_verified.label("is_verified"),
            func.coalesce(sessions_sq.c.total_sessions, 0).label("total_sessions"),
            func.coalesce(sessions_sq.c.completed_sessions, 0).label("completed_sessions"),
            sessions_sq.c.last_session_at.label("last_session_at"),
            func.coalesce(UserStats.total_annotations, annotations_sq.c.total_annotations, 0).label("total_annotations"),
        )
        .outerjoin(UserStats, UserStats.user_id == User.id)
        .outerjoin(sessions_sq, sessions_sq.c.user_id == User.id)
        .outerjoin(annotations_sq, annotations_sq.c.user_id == User.id)
        .order_by(func.coalesce(UserStats.total_annotations, annotations_sq.c.total_annotations, 0).desc(), User.id.asc())
        .all()
    )

    users: list[AdminUserOverview] = [
        AdminUserOverview(
            user_id=int(r.user_id),
            email=r.email,
            username=r.username,
            is_admin=bool(r.is_admin),
            is_active=bool(r.is_active),
            is_verified=bool(r.is_verified),
            total_sessions=int(r.total_sessions),
            completed_sessions=int(r.completed_sessions),
            total_annotations=int(r.total_annotations),
            last_session_at=r.last_session_at,
        )
        for r in rows
    ]

    return AdminAllUsersOverview(
        total_users=len(users),
        total_annotations=sum(u.total_annotations for u in users),
        total_sessions=sum(u.total_sessions for u in users),
        total_completed_sessions=sum(u.completed_sessions for u in users),
        users=users,
    )
