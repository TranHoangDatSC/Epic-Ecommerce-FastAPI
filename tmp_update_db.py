from app.config import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    try:
        # Check if column exists (Postgres/SQLite syntax varies, but we can just try adding it)
        if "postgresql" in settings.DATABASE_URL:
             conn.execute(text("ALTER TABLE product ADD COLUMN IF NOT EXISTS transfer_method SMALLINT NOT NULL DEFAULT 1"))
             conn.execute(text("ALTER TABLE product ADD CONSTRAINT check_transfer_method CHECK (transfer_method IN (1, 2))"))
        else:
             # SQLite doesn't support ADD COLUMN IF NOT EXISTS or CHECK constraints in ALTER TABLE easily
             # We just try to add it and ignore error if exists
             try:
                 conn.execute(text("ALTER TABLE product ADD COLUMN transfer_method SMALLINT NOT NULL DEFAULT 1"))
             except Exception as e:
                 print(f"Column might already exist in SQLite: {e}")
        conn.commit()
        print("Database updated successfully!")
    except Exception as e:
        print(f"Error updating database: {e}")
