"""
Database seeding script for initial data
Run this after migrations to populate the database with initial/sample data
"""

from sqlalchemy.orm import Session
from services.database import SessionLocal, engine
from models.user import User, Question, Image
from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user(db: Session):
    """Create a default admin user"""
    admin = db.query(User).filter(User.email == "admin@captcha.local").first()
    if admin:
        print("✓ Admin user already exists")
        return admin

    admin = User(
        email="admin@captcha.local",
        username="admin",
        hashed_password=pwd_context.hash("admin123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_admin=True,
        is_verified=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("✓ Created admin user (email: admin@captcha.local, password: admin123)")
    return admin


def create_test_user(db: Session):
    """Create a test user"""
    test_user = db.query(User).filter(User.email == "test@captcha.local").first()
    if test_user:
        print("✓ Test user already exists")
        return test_user

    test_user = User(
        email="test@captcha.local",
        username="testuser",
        hashed_password=pwd_context.hash("test123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_admin=False,
        is_verified=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print("✓ Created test user (email: test@captcha.local, password: test123)")
    return test_user


def create_sample_questions(db: Session):
    """Create sample questions"""
    existing_count = db.query(Question).count()
    if existing_count > 0:
        print(f"✓ {existing_count} questions already exist")
        return

    sample_questions = [
        Question(
            question_text="Select all images showing dental cavities",
            question_type="multiple_choice",
            active=True
        ),
        Question(
            question_text="Select all images showing healthy teeth",
            question_type="multiple_choice",
            active=True
        ),
        Question(
            question_text="Select all X-ray images",
            question_type="multiple_choice",
            active=True
        ),
        Question(
            question_text="Select all images showing dental implants",
            question_type="multiple_choice",
            active=True
        ),
    ]

    for question in sample_questions:
        db.add(question)

    db.commit()
    print(f"✓ Created {len(sample_questions)} sample questions")


def seed_database():
    """Main seeding function"""
    print("\n🌱 Seeding database...\n")

    db = SessionLocal()
    try:
        # Create users
        create_admin_user(db)
        create_test_user(db)

        # Create sample questions
        create_sample_questions(db)

        # Note: Images are uploaded via S3, so we don't seed them here
        image_count = db.query(Image).count()
        print(f"✓ Database has {image_count} images")

        print("\n✅ Database seeding completed!\n")
        print("You can login with:")
        print("  Admin: admin@captcha.local / admin123")
        print("  Test:  test@captcha.local / test123")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
