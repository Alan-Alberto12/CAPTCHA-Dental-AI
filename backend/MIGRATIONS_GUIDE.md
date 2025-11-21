# Database Migrations Guide

This project uses **Alembic** for database migrations. This guide will help you understand and use migrations effectively.

## What are Database Migrations?

Database migrations are version-controlled changes to your database schema. They allow you to:
- Track database schema changes over time
- Share schema changes with your team via Git
- Apply changes consistently across different environments (dev, staging, production)
- Rollback changes if needed

## Quick Start

### 1. View Current Migration Status

```bash
./migrate.sh current
```

### 2. Create a New Migration

After modifying models in `models/user.py`, create a migration:

```bash
./migrate.sh create "Add email verification field"
```

This will:
- Auto-generate a migration file in `alembic/versions/`
- Detect changes between your models and database
- Create `upgrade()` and `downgrade()` functions

**IMPORTANT**: Always review the generated migration file before applying it!

### 3. Apply Migrations

Apply all pending migrations to the database:

```bash
./migrate.sh upgrade
```

### 4. View Migration History

```bash
./migrate.sh history
```

## Common Workflows

### Adding a New Column

1. **Modify the model** in `models/user.py`:
   ```python
   class User(Base):
       # ... existing fields ...
       phone_number = Column(String, nullable=True)  # New field
   ```

2. **Create migration**:
   ```bash
   ./migrate.sh create "Add phone_number to users table"
   ```

3. **Review the generated file** in `alembic/versions/`:
   ```python
   def upgrade() -> None:
       op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))

   def downgrade() -> None:
       op.drop_column('users', 'phone_number')
   ```

4. **Apply the migration**:
   ```bash
   ./migrate.sh upgrade
   ```

### Creating a New Table

1. **Add new model** in `models/user.py`:
   ```python
   class UserProfile(Base):
       __tablename__ = "user_profiles"
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       bio = Column(Text)
   ```

2. **Import in env.py** if not already imported (check `alembic/env.py`)

3. **Create migration**:
   ```bash
   ./migrate.sh create "Add user_profiles table"
   ```

4. **Apply migration**:
   ```bash
   ./migrate.sh upgrade
   ```

### Rolling Back a Migration

If you need to undo the last migration:

```bash
./migrate.sh downgrade
```

To downgrade to a specific revision:

```bash
./migrate.sh downgrade abc123def
```

## Team Collaboration

### When Someone Else Creates a Migration

1. **Pull the latest code** (including new migration files):
   ```bash
   git pull origin main
   ```

2. **Apply the migrations**:
   ```bash
   ./migrate.sh upgrade
   ```

Your database will now match theirs!

### Before Creating a Pull Request

1. **Create migrations** for your schema changes:
   ```bash
   ./migrate.sh create "Description of your changes"
   ```

2. **Review the generated migration file**

3. **Test the migration**:
   ```bash
   ./migrate.sh upgrade
   ./migrate.sh downgrade  # Test rollback
   ./migrate.sh upgrade    # Re-apply
   ```

4. **Commit the migration file**:
   ```bash
   git add alembic/versions/*.py
   git commit -m "Add migration: Description of your changes"
   ```

## Migration Script Commands

| Command | Description | Example |
|---------|-------------|---------|
| `create` | Create new migration | `./migrate.sh create "Add user role"` |
| `upgrade` | Apply all pending migrations | `./migrate.sh upgrade` |
| `downgrade` | Rollback migrations | `./migrate.sh downgrade` |
| `current` | Show current revision | `./migrate.sh current` |
| `history` | Show all migrations | `./migrate.sh history` |
| `stamp` | Mark DB at specific revision (without running) | `./migrate.sh stamp head` |
| `help` | Show help message | `./migrate.sh help` |

## Advanced Usage

### Manual Migration Creation

Sometimes autogenerate doesn't capture everything (like data migrations):

```bash
docker exec captcha-dental-backend alembic revision -m "Migrate user data"
```

Then manually edit the generated file in `alembic/versions/`.

### Stamping the Database

If you already have a database with the correct schema and want to start using migrations:

```bash
./migrate.sh stamp head
```

This marks the database as being at the latest migration without running any migrations.

## Troubleshooting

### "Target database is not up to date"

**Problem**: Database is behind the code migrations.

**Solution**:
```bash
./migrate.sh upgrade
```

### "Can't locate revision identified by 'xyz'"

**Problem**: Migration file is missing.

**Solution**: Make sure you've pulled all migration files from Git:
```bash
git pull origin main
./migrate.sh upgrade
```

### "Multiple head revisions are present"

**Problem**: Conflicting migrations from different branches.

**Solution**: Merge the migrations:
```bash
docker exec captcha-dental-backend alembic merge heads -m "Merge migrations"
./migrate.sh upgrade
```

### Autogenerate Didn't Detect My Changes

**Problem**: Alembic didn't detect model changes.

**Common Causes**:
- Model not imported in `alembic/env.py`
- Using types that Alembic doesn't recognize
- Changes to data, not schema

**Solution**: Check `alembic/env.py` imports and create a manual migration if needed.

## Best Practices

1. **Always review generated migrations** before applying them
2. **One logical change per migration** (easier to understand and rollback)
3. **Test both upgrade and downgrade** before committing
4. **Use descriptive migration messages** ("Add user email verification" not "update model")
5. **Never edit applied migrations** - create a new migration instead
6. **Commit migrations with your code changes** in the same PR
7. **Make migrations reversible** when possible (good downgrade functions)

## File Structure

```
backend/
├── alembic/
│   ├── versions/           # Migration files (commit these!)
│   │   └── 9209a434d045_initial_migration.py
│   ├── env.py             # Alembic environment config
│   ├── script.py.mako     # Migration template
│   └── README
├── alembic.ini            # Alembic configuration
├── migrate.sh             # Helper script (this!)
└── models/
    └── user.py            # Your SQLAlchemy models
```

## FAQ

**Q: Do I need to create migrations for every model change?**
A: Yes! All schema changes should have corresponding migrations.

**Q: Should migration files be committed to Git?**
A: Yes! Migration files are part of your codebase.

**Q: Can I delete old migrations?**
A: Generally no, once applied. They form a history of your database schema.

**Q: What if I made a mistake in a migration that's already applied?**
A: Create a new migration to fix it. Don't edit the original.

**Q: How do I share my database changes with the team?**
A: Create a migration, commit it, push it. They pull and run `./migrate.sh upgrade`.

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
