# Quick Database Sync

**For teammates who already have the project and want to sync their database structure.**

## Two Commands

```bash
git pull origin main
./migrate.sh upgrade
```

That's it! ✅

---

## What This Does

- ✅ Gets the latest migration files from Git
- ✅ Updates your database structure to match the team
- ✅ **Keeps all your existing data**
- ✅ Works even if you have different data than others

---

## First Time?

If this is your first time syncing after migrations were added:

```bash
# Tell the system your database is current
./migrate.sh stamp head

# Verify
./migrate.sh current
# Should show: 9209a434d045 (head)
```

Now future syncs will work with just:
```bash
git pull origin main
./migrate.sh upgrade
```

---

## After Every Pull

Make it a habit:
```bash
git pull origin main
cd backend
./migrate.sh upgrade
```

Your database automatically stays in sync! 🎉

---

**Need more details?** See [UPDATE_DATABASE_STRUCTURE.md](UPDATE_DATABASE_STRUCTURE.md)
