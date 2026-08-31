import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# Uses DATABASE_URL environment variable if present (for PostgreSQL), otherwise falls back to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

engine_kwargs = (
    {"connect_args": {"check_same_thread": False, "timeout": 15}}
    if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Enable WAL mode for SQLite so readers don't block writers
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=15000;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()