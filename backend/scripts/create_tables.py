"""
Create all database tables for the teeth segmentation system

This script creates all the necessary database tables including:
- datasets
- images
- annotations
- predictions
- segmentation_models

Usage:
    python scripts/create_tables.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import engine, Base
from models import (
    User,
    Dataset,
    Image,
    Annotation,
    Prediction,
    SegmentationModel,
)


def create_tables():
    """Create all database tables"""
    print("=" * 60)
    print("Creating Database Tables")
    print("=" * 60)

    try:
        # Import all models to ensure they're registered
        models = [
            User,
            Dataset,
            Image,
            Annotation,
            Prediction,
            SegmentationModel,
        ]

        print("\nRegistered models:")
        for model in models:
            print(f"  - {model.__tablename__}")

        # Create all tables
        print("\nCreating tables...")
        Base.metadata.create_all(bind=engine)

        print("\n✓ All tables created successfully!")

        # Verify tables exist
        print("\nVerifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        print("\nExisting tables in database:")
        for table in existing_tables:
            print(f"  ✓ {table}")

        # Check for expected tables
        expected_tables = [model.__tablename__ for model in models]
        missing_tables = set(expected_tables) - set(existing_tables)

        if missing_tables:
            print(f"\n⚠ Warning: Missing tables: {missing_tables}")
        else:
            print("\n✅ All expected tables exist!")

        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_tables()
