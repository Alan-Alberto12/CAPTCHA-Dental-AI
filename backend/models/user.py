from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    #connects users to their sessions and stats
    sessions = relationship("AnnotationSession", back_populates="user", cascade="all, delete-orphan")
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="Cascade"), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires = Column(DateTime(timezone=True), nullable=False)

class EmailConfirmationToken(Base):
    __tablename__ = "email_confirmation_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

#additional models for images, questions, sessions and annotations
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # e.g. "tooth_number", "cavity_detection"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnnotationSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Session metadata
    title = Column(String(100), nullable=True)

    # Session status
    is_completed = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    session_images = relationship("SessionImage", back_populates="session", cascade="all, delete-orphan")
    session_questions = relationship("SessionQuestion", back_populates="session", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="session", cascade="all, delete-orphan")


class SessionImage(Base):
    """Junction table linking sessions to their images"""
    __tablename__ = "session_images"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    image_order = Column(Integer, nullable=False)  # Display order in the session
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("AnnotationSession", back_populates="session_images")
    image = relationship("Image")


class SessionQuestion(Base):
    """Junction table linking sessions to their questions"""
    __tablename__ = "session_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    question_order = Column(Integer, nullable=False)  # Order of question in the session (1, 2, 3, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("AnnotationSession", back_populates="session_questions")
    question = relationship("Question")


class Annotation(Base):
    """User's answer to a question - which images they selected"""
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))

    # Metadata about the annotation
    is_correct = Column(Boolean, nullable=True)
    time_spent = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("AnnotationSession", back_populates="annotations")
    question = relationship("Question")
    selected_images = relationship("AnnotationImage", back_populates="annotation", cascade="all, delete-orphan")


class AnnotationImage(Base):
    """Which images the user selected for a specific annotation"""
    __tablename__ = "annotation_images"

    id = Column(Integer, primary_key=True, index=True)
    annotation_id = Column(Integer, ForeignKey("annotations.id", ondelete="CASCADE"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    annotation = relationship("Annotation", back_populates="selected_images")
    image = relationship("Image")


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    total_points = Column(Integer, default=0)
    total_annotations = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    daily_streak = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="stats")


class Prediction(Base):
    """CNN prediction result for an image"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String, nullable=False)         # e.g. "resnet50"
    predicted_label = Column(String, nullable=False)     # "needs_review" or "no_review"
    confidence = Column(Float, nullable=False)           # softmax probability
    model_version = Column(String, nullable=True)        # .pth filename
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    image = relationship("Image")

class PointTransaction(Base):
    """Logs every individual point event for a user"""
    __tablename__ = "point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)  # e.g. "session_complete", "streak_7", "volume_3"
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class DailySessionCount(Base):
    """Tracks how many sessions a user completed on each calendar day"""
    __tablename__ = "daily_session_counts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)  # just the date portion matters
    session_count = Column(Integer, default=0)

    user = relationship("User")
