# Team Setup Guide

This guide helps new team members get the database set up on their local machine.

## Quick Setup (Recommended)

If you're setting up the project for the first time, just run:

```bash
cd backend
./setup_database.sh
```

This script will:
1. ✓ Check Docker is running
2. ✓ Start all containers (database, backend, frontend)
3. ✓ Apply all database migrations
4. ✓ Seed the database with initial data

**That's it!** You'll have a working database with:
- Admin user: `admin@captcha.local` / `admin123`
- Test user: `test@captcha.local` / `test123`
- Sample questions
- Your existing images (upload via admin panel)

## Manual Setup

If you prefer to set up step-by-step:

### 1. Start Docker containers
```bash
docker-compose up -d
```

### 2. Apply migrations
```bash
cd backend
./migrate.sh upgrade
```

### 3. (Optional) Seed with initial data
```bash
docker exec captcha-dental-backend python seed_data.py
```

## Staying in Sync

When a teammate creates new migrations:

```bash
# Pull the latest code
git pull origin main

# Apply new migrations
./migrate.sh upgrade
```

Your database will automatically update to match!

## Resetting Your Database

If you need to start fresh:

```bash
# Stop containers
docker-compose down -v

# Start fresh
./setup_database.sh
```

The `-v` flag removes all data volumes, giving you a completely clean slate.

## Troubleshooting

### "No migrations to apply"
This is fine! It means your database is already up to date.

### "Database connection refused"
Make sure Docker is running:
```bash
docker ps
```

You should see containers for `db`, `backend`, `frontend`, and `mailhog`.

### "Migration file not found"
Make sure you've pulled all changes from Git:
```bash
git pull origin main
```

### "Permission denied" on scripts
Make the scripts executable:
```bash
chmod +x migrate.sh setup_database.sh
```

## What Gets Shared?

### ✅ Shared via Git (version controlled)
- Database structure (via migrations in `alembic/versions/`)
- Code changes
- Configuration files

### ❌ NOT Shared (local only)
- Actual data in your database
- `.env` file (contains secrets)
- Uploaded images (stored in AWS S3)

## For Production Deployment

See `MIGRATIONS_GUIDE.md` for production deployment strategies.

In production, you would:
1. Apply migrations: `./migrate.sh upgrade`
2. Run custom seed scripts if needed
3. Never use the development seed data (admin123 passwords, etc.)
