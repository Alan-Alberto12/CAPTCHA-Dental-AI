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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    #connects users to their annotations and stats
    annotations = relationship("Annotation", back_populates="user", cascade="all, delete-orphan")
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

#additional models for images, challenges, annotations and user stats
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=False)
    question_type = Column(String, nullable=False)  # e.g. "tooth_number", "crack_detection"
    question_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    challenges = relationship("Challenge", back_populates="image")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    image = relationship("Image", back_populates="challenges")
    annotations = relationship("Annotation", back_populates="challenge", cascade="all, delete-orphan")


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"))
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    time_spent = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="annotations")
    challenge = relationship("Challenge", back_populates="annotations")


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

