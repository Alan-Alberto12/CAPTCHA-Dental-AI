# Database Schema Setup Guide

This guide explains how to set up the database with the correct schema.

## Option 1: Using Alembic Migrations (Recommended)

This is the preferred method as it keeps track of schema versions.

```bash
# 1. Pull latest code
git pull origin Yased-Branch

# 2. Stop and remove containers
docker compose down

# 3. Remove old database volume (WARNING: deletes all data)
docker volume rm captcha-dental-ai_postgres_data

# 4. Start containers
docker compose up -d

# 5. Wait for database to be ready (about 10 seconds)
sleep 10

# 6. Run all migrations
docker compose exec backend alembic upgrade head
```

## Option 2: Using Schema SQL File (Direct Import)

If migrations are causing issues, you can directly import the schema:

```bash
# 1. Stop and remove containers
docker compose down

# 2. Remove old database volume (WARNING: deletes all data)
docker volume rm captcha-dental-ai_postgres_data

# 3. Start containers
docker compose up -d

# 4. Wait for database to be ready
sleep 10

# 5. Import schema directly
docker compose exec -T db psql -U captcha_user -d captcha_dental_db < backend/database_schema.sql

# 6. Mark migrations as applied (so Alembic knows the current state)
docker compose exec backend alembic stamp head
```

## Verify Database Schema

After setup, verify the schema is correct:

```bash
# Connect to database
docker exec -it captcha-dental-db psql -U captcha_user -d captcha_dental_db

# List all tables
\dt

# View specific table structure (example: images)
\d images

# Exit
\q
```

## Expected Tables

Your database should have these 13 tables:

1. `alembic_version` - Migration version tracking
2. `users` - User accounts
3. `password_reset_tokens` - Password reset functionality
4. `email_confirmation_tokens` - Email verification
5. `user_data_consent` - User consent tracking
6. `user_stats` - User statistics
7. `images` - Dental images for annotation
8. `questions` - Questions for annotation sessions
9. `sessions` - Annotation sessions
10. `session_images` - Images in each session
11. `session_questions` - Questions in each session
12. `annotations` - User answers to questions
13. `annotation_images` - Images selected for each annotation

## Images Table Structure

The `images` table should have these columns:
- `id` (integer, primary key)
- `filename` (character varying, not null, unique)
- `image_url` (character varying, not null)
- `created_at` (timestamp with time zone, default now())

**Note:** The `images` table should NOT have `question_type` or `question_text` columns. Those belong in the `questions` table.

## Troubleshooting

### Migration Errors

If you get migration errors:
1. Check which migration you're on: `docker compose exec backend alembic current`
2. View migration history: `docker compose exec backend alembic history`
3. If stuck, use Option 2 (direct schema import)

### Column Mismatch Errors

If you have extra columns (like `question_type` in `images` table):
1. The latest migration should fix this automatically
2. If not, manually drop incorrect columns:
   ```sql
   ALTER TABLE images DROP COLUMN IF EXISTS question_type;
   ALTER TABLE images DROP COLUMN IF EXISTS question_text;
   ```

### Clean Slate

To completely start over:
```bash
docker compose down -v
docker compose up -d
sleep 10
docker compose exec backend alembic upgrade head
```

## After Setup

1. Create an admin user account
2. Import test images (if needed)
3. Import test questions (if needed)

To promote a user to admin:
```bash
docker exec -it captcha-dental-db psql -U captcha_user -d captcha_dental_db \
  -c "UPDATE users SET is_admin = true WHERE email = 'your_email@example.com';"
```
