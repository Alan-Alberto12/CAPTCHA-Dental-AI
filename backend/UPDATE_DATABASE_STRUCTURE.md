# Update Your Database Structure

**For team members who already have the project set up and want to sync their database structure.**

## Quick Update (Recommended)

If you already have the project and just need to update your database structure:

```bash
# 1. Pull the latest migration files
git pull origin main

# 2. Apply the migrations
cd backend
./migrate.sh upgrade
```

✅ **Done!** Your database structure now matches the team's.

**This will:**
- ✅ Update your database structure
- ✅ Keep all your existing data
- ✅ Preserve your local changes
- ✅ Work even if your database has different data

---

## What If I Get Conflicts?

### "Already up to date"
```
INFO  [alembic.runtime.migration] Running upgrade  -> 9209a434d045
```
This is good! Your database is already current.

### "Can't locate revision"
This means your database doesn't know what version it's at.

**Check current status:**
```bash
./migrate.sh current
```

**If it shows nothing**, stamp it to mark where you are:
```bash
# This tells the migration system "my database is already current"
./migrate.sh stamp head
```

Then check status again:
```bash
./migrate.sh current
```

You should see: `9209a434d045 (head)`

---

## Detailed Steps

### Step 1: Check Your Current Migration Status

```bash
cd backend
./migrate.sh current
```

**Possible outputs:**

#### A) Shows nothing (blank)
Your database exists but isn't tracked by migrations yet.

**Solution:**
```bash
# Mark your database as current (since you already have the tables)
./migrate.sh stamp head
./migrate.sh current  # Should now show: 9209a434d045 (head)
```

#### B) Shows a revision number
```
9209a434d045 (head)
```
Great! You're tracked and current.

#### C) Shows an older revision
```
abc123def (not head)
```
You're behind. Just run:
```bash
./migrate.sh upgrade
```

### Step 2: Pull Latest Migration Files

```bash
git pull origin main
```

This gets all new migration files from the team.

### Step 3: Apply New Migrations

```bash
./migrate.sh upgrade
```

This updates your database structure to match the team's.

### Step 4: Verify

```bash
./migrate.sh current
```

Should show the latest revision with `(head)`.

---

## Common Scenarios

### Scenario 1: "I have the old database structure"

```bash
git pull origin main
./migrate.sh upgrade
```

Your database will automatically update to the new structure!

### Scenario 2: "I just pulled new migration files"

```bash
./migrate.sh upgrade
```

Applies all new migrations since your last update.

### Scenario 3: "I have tables but no migration tracking"

This happens if you created tables before migrations were set up.

```bash
# Mark your current state
./migrate.sh stamp head

# Future updates will work normally
./migrate.sh upgrade
```

### Scenario 4: "I want to start completely fresh"

```bash
# Nuclear option - deletes everything
docker-compose down -v
./setup_database.sh
```

⚠️ **Warning:** This deletes all your data!

---

## What Gets Updated?

When you run `./migrate.sh upgrade`, Alembic will:

✅ **Add new tables** if they don't exist
✅ **Add new columns** to existing tables
✅ **Create new indexes** and constraints
✅ **Preserve all your existing data**

❌ **Will NOT:**
- Delete your data
- Overwrite existing data
- Change your local files
- Affect uncommitted code changes

---

## Troubleshooting

### Error: "Target database is not up to date"

**Cause:** Your database is behind the migrations.

**Fix:**
```bash
./migrate.sh upgrade
```

### Error: "Multiple head revisions are present"

**Cause:** Conflicting migrations from different branches.

**Fix:**
```bash
docker exec captcha-dental-backend alembic merge heads -m "Merge migrations"
./migrate.sh upgrade
```

### Error: "Can't connect to database"

**Cause:** Docker isn't running.

**Fix:**
```bash
docker-compose up -d
# Wait 5 seconds for database to start
./migrate.sh upgrade
```

### Error: "Permission denied: ./migrate.sh"

**Fix:**
```bash
chmod +x migrate.sh
./migrate.sh upgrade
```

---

## Daily Workflow

Every time you pull code:

```bash
git pull origin main
./migrate.sh upgrade  # Apply any new database changes
```

That's it! Your database stays in sync with the team automatically.

---

## Need Help?

- **Migration basics:** See [MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md)
- **First time setup:** See [TEAM_SETUP.md](TEAM_SETUP.md)
- **Sharing options:** See [DATABASE_SHARING_OPTIONS.md](DATABASE_SHARING_OPTIONS.md)
