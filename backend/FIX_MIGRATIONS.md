# Fix Migration Issues - Outdated Columns

## The Problem

Your teammate got the tables created but with outdated columns. This happens because:

1. The initial migration was created when tables already existed
2. Alembic saw "no changes" and created an empty migration
3. When teammates run it, it creates basic tables but doesn't know what columns should exist

## The Solution

Create a **proper initial migration** that captures the full current schema.

---

## Steps to Fix (For You - The Database Owner)

### 1. Delete the Empty Migration

```bash
cd backend
rm alembic/versions/9209a434d045_initial_migration.py
rm -rf alembic/versions/__pycache__
```

### 2. Drop and Recreate Alembic Version Table

This forces Alembic to create a fresh migration:

```bash
# Enter database
docker exec -it captcha-dental-db psql -U captcha_user -d captcha_dental_db

# Inside psql:
DROP TABLE IF EXISTS alembic_version;
\q
```

### 3. Create Proper Initial Migration

```bash
# Create migration by comparing to empty database
docker exec captcha-dental-backend alembic revision --autogenerate -m "Initial complete schema"
```

### 4. Verify the Migration Has Content

```bash
# Check the new migration file
cat alembic/versions/*_initial_complete_schema.py
```

**You should see:**
- `CREATE TABLE` statements
- All columns defined
- Foreign keys
- Indexes
- NOT just `pass`

### 5. Stamp Your Database

Since you already have the correct schema:

```bash
./migrate.sh stamp head
```

### 6. Commit and Push

```bash
git add alembic/versions/
git commit -m "Add proper initial migration with complete schema"
git push
```

---

## Steps for Your Teammates

### Option A: Fresh Start (Recommended)

```bash
# 1. Pull latest code
git pull origin main

# 2. Delete old database
docker-compose down -v

# 3. Fresh setup
cd backend
./setup_database.sh
```

### Option B: Keep Existing Data

If they have data they want to keep:

```bash
# 1. Pull latest code
git pull origin main

# 2. Check current migration status
./migrate.sh current

# 3. Manually apply the schema changes
# See "Manual Schema Update" section below
```

---

## Manual Schema Update (For Teammates Keeping Data)

If the migration doesn't work, they can manually update their database:

### Connect to Database:
```bash
docker exec -it captcha-dental-db psql -U captcha_user -d captcha_dental_db
```

### Check What Columns Exist:
```sql
-- Check users table
\d users

-- Check all tables
\dt

-- Check specific table structure
\d+ sessions
```

### Add Missing Columns:

Compare their schema to yours and add missing columns:

```sql
-- Example: If they're missing updated_at in users
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Example: If they're missing is_verified in users
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;

-- Check images table
ALTER TABLE images ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Check questions table
ALTER TABLE questions ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT true;
ALTER TABLE questions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Check sessions table
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS is_completed BOOLEAN DEFAULT false;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;

-- Check annotations table
ALTER TABLE annotations ADD COLUMN IF NOT EXISTS is_correct BOOLEAN;
ALTER TABLE annotations ADD COLUMN IF NOT EXISTS time_spent FLOAT;
ALTER TABLE annotations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Check user_stats table
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS total_annotations INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS accuracy_rate FLOAT DEFAULT 0.0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS daily_streak INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Exit
\q
```

Then stamp the database:
```bash
./migrate.sh stamp head
```

---

## Prevention for Future

### When Adding New Columns:

**Step 1: Modify the model** (e.g., `models/user.py`)
```python
class User(Base):
    # ... existing columns ...
    new_column = Column(String, nullable=True)  # Add this
```

**Step 2: Create migration**
```bash
./migrate.sh create "Add new_column to users"
```

**Step 3: Review the migration file**
```python
# alembic/versions/xyz_add_new_column.py
def upgrade():
    op.add_column('users', sa.Column('new_column', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'new_column')
```

**Step 4: Test both directions**
```bash
./migrate.sh upgrade    # Apply
./migrate.sh downgrade  # Rollback
./migrate.sh upgrade    # Re-apply
```

**Step 5: Commit**
```bash
git add alembic/versions/
git add models/user.py
git commit -m "Add new_column to users table"
git push
```

**Step 6: Teammates update**
```bash
git pull
./migrate.sh upgrade
```

---

## Common Issues

### "Already exists" Errors

If teammate runs migration and gets "column already exists":

**Option 1: Skip the migration**
```bash
# Mark it as applied without running it
./migrate.sh stamp head
```

**Option 2: Edit migration to use IF NOT EXISTS**
```python
# In the migration file
def upgrade():
    # Instead of:
    op.add_column('users', ...)

    # Use:
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS column_name TYPE;
    """)
```

### Migration Out of Order

If migrations were applied in wrong order:

```bash
# Check history
./migrate.sh history

# Downgrade to specific version
./migrate.sh downgrade abc123

# Re-upgrade
./migrate.sh upgrade
```

### Database State Unknown

If completely lost track:

```bash
# Nuclear option - fresh start
docker-compose down -v
./setup_database.sh
```

---

## Best Practices

1. ✅ **Always create migrations for schema changes**
2. ✅ **Test both upgrade and downgrade**
3. ✅ **Review generated migrations before committing**
4. ✅ **Use descriptive migration messages**
5. ✅ **Never edit applied migrations**
6. ✅ **Commit migrations with model changes**
7. ✅ **Use `IF NOT EXISTS` for idempotency**

---

## Quick Reference

```bash
# Create migration
./migrate.sh create "Description"

# Apply migrations
./migrate.sh upgrade

# Check status
./migrate.sh current

# View history
./migrate.sh history

# Rollback one
./migrate.sh downgrade

# Mark as current (without running)
./migrate.sh stamp head

# Fresh start
docker-compose down -v && ./setup_database.sh
```

---

## Summary

**Your action:**
1. Delete empty migration
2. Create proper migration with full schema
3. Stamp your database
4. Commit and push

**Teammates action:**
1. Pull your code
2. Fresh start: `docker-compose down -v && ./setup_database.sh`
3. Or manual SQL updates + stamp

This will ensure everyone has the same schema! 🎉
