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
    """Create questions"""
    existing_count = db.query(Question).count()
    if existing_count > 0:
        print(f"✓ {existing_count} questions already exist")
        return

    questions = [
        # Realism (parent)
        Question(question_text="Select the following images that are realistic", question_type="realistic", active=True),
        # Anatomy (parent)
        Question(question_text="Select the following images that are anatomically accurate", question_type="anatomic", active=True),
        # Clinical (parent)
        Question(question_text="Select the following images that are clinically acceptable", question_type="clinical", active=True),
        # Realism sub-questions
        Question(question_text="Select the images where lighting and shadows are consistent with the light source", question_type="realistic_type", active=True),
        Question(question_text="Select the images where textures appear natural and non-synthetic", question_type="realistic_type", active=True),
        Question(question_text="Select the images where proportions match real-world scale", question_type="realistic_type", active=True),
        Question(question_text="Select the images free from visible rendering artifacts or digital distortion", question_type="realistic_type", active=True),
        Question(question_text="Select the images where depth and perspective appear spatially accurate", question_type="realistic_type", active=True),
        Question(question_text="Select the images where background and foreground elements are cohesive", question_type="realistic_type", active=True),
        # Anatomy sub-questions
        Question(question_text="Select the images where bone structure and skeletal alignment are correct", question_type="anatomic_type", active=True),
        Question(question_text="Select the images where muscle groups are correctly placed and shaped", question_type="anatomic_type", active=True),
        Question(question_text="Select the images where joint positions fall within normal range of motion", question_type="anatomic_type", active=True),
        Question(question_text="Select the images where organ size and placement are consistent with standard anatomy", question_type="anatomic_type", active=True),
        Question(question_text="Select the images where symmetry is appropriate for the structure depicted", question_type="anatomic_type", active=True),
        Question(question_text="Select the images where vascular or nerve pathways are correctly represented", question_type="anatomic_type", active=True),
        # Clinical sub-questions
        Question(question_text="Select the images with sufficient resolution and clarity for diagnostic use", question_type="clinical_type", active=True),
        Question(question_text="Select the images free from motion blur, noise, or imaging artifacts", question_type="clinical_type", active=True),
        Question(question_text="Select the images with appropriate contrast and exposure for the structure of interest", question_type="clinical_type", active=True),
        Question(question_text="Select the images where the region of interest is fully within the frame", question_type="clinical_type", active=True),
        Question(question_text="Select the images that meet standard positioning and orientation protocols", question_type="clinical_type", active=True),
        Question(question_text="Select the images where image labeling and annotations are accurate and complete", question_type="clinical_type", active=True),
        Question(question_text="Select the images suitable for use in a clinical report or patient record", question_type="clinical_type", active=True),
    ]

    for question in questions:
        db.add(question)

    db.commit()
    print(f"✓ Created {len(questions)} questions")


def seed_images(db: Session):
    """Seed S3 images"""
    existing_count = db.query(Image).count()
    if existing_count > 0:
        print(f"✓ {existing_count} images already exist")
        return

    base_url = "https://captcha-dental-images.s3.us-east-2.amazonaws.com/test/good_quality_test/"
    filenames = [
        "DIG01_C1sDR (10).jpeg", "DIG01_C1sDR (11).jpeg", "DIG01_C1sDR (12).jpeg",
        "DIG01_C1sDR (14).jpeg", "DIG01_C1sDR (15).jpeg", "DIG01_C1sDR (2).jpeg",
        "DIG01_C1sDR (20).jpeg", "DIG01_C1sDR (21).jpeg", "DIG01_C1sDR (23).jpeg",
        "DIG01_C1sDR (24).jpeg", "DIG01_C1sDR (32).jpeg", "DIG01_C1sDR (37).jpeg",
        "DIG01_C1sDR (38).jpeg", "DIG01_C1sDR (69).jpeg", "DIG01_C2sDR (32).jpeg",
        "DIG01_C2sDR (33).jpeg", "DIG01_C2sDR (34).jpeg", "DIG01_C2sDR (49).jpeg",
        "DIG01_C2sDR (5).jpeg", "DIG02_C1sDR (2).jpeg", "DIG02_C1sDR (20).jpeg",
        "DIG02_C1sDR (21).jpeg", "DIG02_C1sDR (52).jpeg", "DIG02_C1sDR (57).jpeg",
        "DIG02_C1sDR (65).jpeg", "DIG02_C1sDR (93).jpeg", "DIG02_C1sDR (94).jpeg",
        "DIG02_C2sDR (38).jpeg", "DIG02_C2sDR (39).jpeg", "DIG02_C2sDR (50).jpeg",
        "DIG02_C2sDR (51).jpeg", "DIG02_C2sDR (52).jpeg", "DIG02_C2sDR (57).jpeg",
        "DIG02_C2sDR (58).jpeg", "DIG02_C2sDR (59).jpeg", "DIG02_C2sDR (64).jpeg",
        "DIG02_C2sDR (74).jpeg", "DIG02_C2sDR (80).jpeg", "DIG02_C2sDR (81).jpeg",
        "DIG02_C2sDR (85).jpeg", "DIG02_C2sDR (87).jpeg", "DIG02_C2sDR (88).jpeg",
        "DIG02_C2sDR (96).jpeg", "DIG02_C2sDR (97).jpeg", "DIG02_C2sDR (99).jpeg",
        "DIG03_C1sDR (125).jpeg", "DIG03_C1sDR (126).jpeg", "DIG03_C1sDR (131).jpeg",
        "DIG03_C1sDR (132).jpeg", "DIG03_C1sDR (156).jpeg", "DIG03_C1sDR (157).jpeg",
        "DIG03_C1sDR (161).jpeg", "DIG03_C1sDR (162).jpeg", "DIG03_C1sDR (165).jpeg",
        "DIG03_C1sDR (166).jpeg", "DIG03_C1sDR (167).jpeg", "DIG03_C1sDR (17).jpeg",
        "DIG03_C1sDR (170).jpeg", "DIG03_C1sDR (174).jpeg", "DIG03_C1sDR (175).jpeg",
        "DIG03_C1sDR (191).jpeg", "DIG03_C1sDR (192).jpeg", "DIG03_C1sDR (193).jpeg",
        "DIG03_C1sDR (198).jpeg", "DIG03_C1sDR (199).jpeg", "DIG03_C1sDR (285).jpeg",
        "DIG03_C1sDR (286).jpeg", "DIG03_C1sDR (3).jpeg", "DIG03_C1sDR (30).jpeg",
        "DIG03_C1sDR (326).jpeg", "DIG03_C1sDR (327).jpeg", "DIG03_C1sDR (332).jpeg",
        "DIG03_C1sDR (333).jpeg", "DIG03_C1sDR (334).jpeg", "DIG03_C1sDR (35).jpeg",
        "DIG03_C1sDR (350).jpeg", "DIG03_C1sDR (36).jpeg", "DIG03_C1sDR (360).jpeg",
        "DIG03_C1sDR (361).jpeg", "DIG03_C1sDR (365).jpeg", "DIG03_C1sDR (366).jpeg",
        "DIG03_C1sDR (6).jpeg", "DIG03_C1sDR (60).jpeg", "DIG03_C1sDR (83).jpeg",
        "DIG03_C1sDR (84).jpeg", "DIG03_C2sDR (11).jpeg", "DIG03_C2sDR (12).jpeg",
        "DIG03_C2sDR (17).jpeg", "DIG03_C2sDR (26).jpeg", "DIG03_C2sDR (27).jpeg",
        "DIG03_C2sDR (32).jpeg", "DIG03_C2sDR (33).jpeg", "DIG03_C2sDR (34).jpeg",
        "DIG03_C2sDR (4).jpeg", "DIG03_C2sDR (40).jpeg", "DIG03_C2sDR (7).jpeg",
        "DIG03_C2sDR (8).jpeg",
    ]

    for filename in filenames:
        db.add(Image(filename=filename, image_url=base_url + filename))

    db.commit()
    print(f"✓ Created {len(filenames)} images")


def seed_database():
    """Main seeding function"""
    print("\n🌱 Seeding database...\n")

    db = SessionLocal()
    try:
        # Create users
        create_admin_user(db)
        create_test_user(db)

        # Create questions
        create_sample_questions(db)

        # Seed images
        seed_images(db)

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
