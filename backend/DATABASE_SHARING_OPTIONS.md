# Database Sharing Options

How to share your current database structure with your team.

## Option 1: Migrations Only (Recommended) ✅

**Best for:** New team members starting fresh

**What they get:**
- ✅ Exact database structure
- ❌ No existing data

**How it works:**
1. They clone the repo (gets all migration files)
2. Run setup script:
   ```bash
   ./setup_database.sh
   ```
3. Their database structure matches yours automatically

**Pros:**
- Clean, version-controlled
- Automatic with Git
- Best practice for development

**Cons:**
- Doesn't include your existing data
- They need to upload images separately

---

## Option 2: Database Dump (Structure + Data)

**Best for:** Sharing existing data with the team

**What they get:**
- ✅ Exact database structure
- ✅ All your data (users, annotations, questions)
- ⚠️  Image URLs only (images are in S3)

**How to create a dump:**

### Full Dump (structure + data):
```bash
docker exec captcha-dental-db pg_dump -U captcha_user -d captcha_dental_db --clean --if-exists > database_full_dump.sql
```

### Structure Only (no data):
```bash
docker exec captcha-dental-db pg_dump -U captcha_user -d captcha_dental_db --clean --if-exists --schema-only > database_schema_dump.sql
```

### Data Only (no structure):
```bash
docker exec captcha-dental-db pg_dump -U captcha_user -d captcha_dental_db --data-only > database_data_dump.sql
```

**How they restore it:**
```bash
# Start Docker
docker-compose up -d

# Wait for database to be ready (about 5 seconds)
sleep 5

# Restore the dump
docker exec -i captcha-dental-db psql -U captcha_user -d captcha_dental_db < database_full_dump.sql

# Mark database with current migration
./migrate.sh stamp head
```

**Pros:**
- Includes all your data
- Quick to restore
- Everyone has identical data for testing

**Cons:**
- Dump file can be large
- Sensitive data might be included (user passwords, emails)
- Not version-controlled in Git (usually added to .gitignore)
- Need to regenerate dump when data changes

---

## Option 3: Hybrid Approach (Best Practice) 🌟

**Best for:** Production-like development workflow

**What they get:**
- ✅ Database structure (via migrations)
- ✅ Initial seed data (via seed script)
- ✅ Version controlled

**How it works:**

1. **You maintain** `seed_data.py` with essential data:
   - Admin users
   - Sample questions
   - Reference data

2. **Team members run**:
   ```bash
   ./setup_database.sh
   ```

3. **Everyone gets**:
   - Same structure
   - Same baseline data
   - Can add their own test data

**Pros:**
- Version controlled (in Git)
- Reproducible
- No sensitive data
- Works for both development and production
- Easy to update

**Cons:**
- Doesn't include your specific test data
- Requires maintaining seed script

---

## Recommendation by Scenario

### Scenario 1: "Team member joining the project"
**Use:** Hybrid Approach (Option 3)
```bash
git clone <repo>
cd backend
./setup_database.sh
```

### Scenario 2: "Want everyone to have the same test data"
**Use:** Database Dump (Option 2)
- Create dump: `docker exec captcha-dental-db pg_dump ... > dump.sql`
- Share via Google Drive/Dropbox (don't commit to Git)
- They restore: `docker exec -i captcha-dental-db psql ... < dump.sql`

### Scenario 3: "Just want the structure, we'll add our own data"
**Use:** Migrations Only (Option 1)
```bash
./setup_database.sh
# Or just: ./migrate.sh upgrade
```

### Scenario 4: "Production deployment"
**Use:** Migrations Only (Option 1)
- NEVER use seed_data.py in production
- Create production-specific seed scripts if needed
- Use environment-specific configuration

---

## Important Notes

### About S3 Images
- Database only stores S3 URLs, not actual images
- Image files are in AWS S3 bucket
- Team members need:
  - AWS credentials in `.env`
  - Access to the same S3 bucket
  - Or upload their own images

### About Sensitive Data
If creating a dump to share:

**⚠️ NEVER commit database dumps to Git if they contain:**
- User passwords (even hashed)
- Real email addresses
- Production data
- API keys or secrets

**Instead:**
- Share dumps via private channels (Google Drive, etc.)
- Sanitize data first
- Use seed_data.py for shareable baseline data

### About .gitignore
Add to your `backend/.gitignore`:
```
# Database dumps
*.sql
database_*.sql
```

---

## What We've Set Up (Current State)

✅ **Migrations:** Working with Alembic
✅ **Migration files:** In Git at `alembic/versions/`
✅ **Seed script:** `seed_data.py` creates admin/test users
✅ **Setup script:** `setup_database.sh` does everything
✅ **Documentation:** This guide + MIGRATIONS_GUIDE.md + TEAM_SETUP.md

**Your team can now:**
1. Clone the repo
2. Run `./setup_database.sh`
3. Start developing with a working database

**The database structure is automatically shared via Git! 🎉**
