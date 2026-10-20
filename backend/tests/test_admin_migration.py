import os
from pathlib import Path
import subprocess
import sys

from sqlalchemy import create_engine, inspect, text


def test_admin_migration_preserves_existing_accounts(tmp_path):
    root = Path(__file__).resolve().parents[1]
    database_url = f"sqlite:///{(tmp_path / 'migration.db').as_posix()}"
    env = {**os.environ, "DATABASE_URL": database_url}

    def migrate(*args):
        result = subprocess.run([sys.executable, "-m", "alembic", *args], cwd=root, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

    migrate("upgrade", "8aaa48b081f8")
    engine = create_engine(database_url)
    with engine.begin() as conn:
        conn.execute(text("""INSERT INTO users (id, email, password_hash, full_name, preferred_language,
            default_currency, timezone, is_active, created_at, updated_at)
            VALUES ('legacy', 'legacy@example.com', 'hashed', 'Legacy Owner', 'en', 'EUR', 'UTC', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""))
    migrate("upgrade", "head")
    with engine.connect() as conn:
        row = conn.execute(text("SELECT account_status, is_admin, email_verified, review_reason FROM users WHERE id='legacy'")).one()
        assert tuple(row) == ("APPROVED", 0, 0, "")
        assert "account_reviews" in inspect(conn).get_table_names()
    migrate("downgrade", "8aaa48b081f8")
    with engine.connect() as conn:
        assert "account_status" not in {c["name"] for c in inspect(conn).get_columns("users")}
        assert conn.execute(text("SELECT email FROM users WHERE id='legacy'")).scalar() == "legacy@example.com"
    engine.dispose()
