# CAPTCHA-Dental-AI
UCF Senior Design 2025 Project: CAPTCHA for Dental AI. Using AI to help gameify, annotating and classifying teeth data.

Roles:
-  Katerina Garkova (PM and Frontend)
-  David Hablich (Frontend)
-  Sebastian Reconco (Frontend)
-  Arique Heemal (Backend & AI)
-  Alan Alberto (Backend & AI)
-  Yased Luna Villanueva (Backend & AI)

Frontend:
    React and React Native

Backend: 
    Python FastAPI, Pydantic, OpenAPI/Swagger, 

Database: 
    PostgreSQL 

AI Learning Models: 
    Pytorch or Tensorflow

(
Image Processing:
    OpenCV, DICOM
)

Extras: 
    Docker, Jira,

## Quick Start

### First Time Setup
```bash
cd backend
./setup_database.sh
```

This will:
- Start all containers (database, backend, frontend)
- Apply database migrations
- Seed with initial test data

### Regular Development
```bash
docker compose up --build
```

To start backend only:
```bash
docker compose up backend
```

## Database Management

We use **Alembic** for database migrations. See [backend/MIGRATIONS_GUIDE.md](backend/MIGRATIONS_GUIDE.md) for details.

### 🔄 For Existing Team Members (Update Your Database)

After pulling new code, sync your database structure:
```bash
cd backend
git pull origin main
./migrate.sh upgrade
```

📖 **Full guide:** [backend/UPDATE_DATABASE_STRUCTURE.md](backend/UPDATE_DATABASE_STRUCTURE.md)

### ✨ Creating New Migrations

After modifying models in `models/user.py`:
```bash
cd backend
./migrate.sh create "Description of change"
./migrate.sh upgrade
git add alembic/versions/*.py
git commit -m "Add migration: Description"
```

### 📋 Common Commands

```bash
cd backend

# Apply pending migrations
./migrate.sh upgrade

# Check current migration status
./migrate.sh current

# View migration history
./migrate.sh history

# Create new migration
./migrate.sh create "message"
```

### 📚 Documentation

- **New team members:** [backend/TEAM_SETUP.md](backend/TEAM_SETUP.md)
- **Update database:** [backend/UPDATE_DATABASE_STRUCTURE.md](backend/UPDATE_DATABASE_STRUCTURE.md)
- **Migration guide:** [backend/MIGRATIONS_GUIDE.md](backend/MIGRATIONS_GUIDE.md)
- **Sharing options:** [backend/DATABASE_SHARING_OPTIONS.md](backend/DATABASE_SHARING_OPTIONS.md)
