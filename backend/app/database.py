"""
Database engine and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.config import get_settings

settings = get_settings()

# SQLite fallback for local dev
if "postgresql" in settings.DATABASE_URL and settings.APP_ENV == "development":
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )
    except Exception:
        # Fallback to SQLite
        import os
        os.makedirs("data", exist_ok=True)
        engine = create_engine(
            "sqlite:///data/stockdb.sqlite",
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
else:
    import os
    os.makedirs("data", exist_ok=True)
    engine = create_engine(
        "sqlite:///data/stockdb.sqlite",
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
