import os
import tempfile
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import get_settings

logger = logging.getLogger("hackthehacker.database")
settings = get_settings()

Base = declarative_base()

def create_db_engine():
    """
    Creates SQLAlchemy engine:
    1. Tries primary PostgreSQL database.
    2. If PostgreSQL is unreachable and fallback enabled, tries local SQLite.
    3. If local file creation is restricted, falls back to tempdir/in-memory SQLite.
    """
    primary_url = settings.DATABASE_URL
    try:
        eng = create_engine(primary_url, pool_pre_ping=True)
        with eng.connect():
            logger.info(f"Connected to primary database: {primary_url.split('@')[-1]}")
            return eng
    except Exception as e:
        logger.warning(f"Primary PostgreSQL not available ({e}). Checking fallback...")
        if settings.USE_SQLITE_FALLBACK:
            # Try configured fallback URL
            fallback_url = settings.SQLITE_FALLBACK_URL
            try:
                eng = create_engine(fallback_url, connect_args={"check_same_thread": False})
                with eng.connect():
                    logger.info(f"Using SQLite database: {fallback_url}")
                    return eng
            except Exception:
                # Use tempdir SQLite
                temp_db = os.path.join(tempfile.gettempdir(), "hackthehacker.db").replace("\\", "/")
                temp_url = f"sqlite:///{temp_db}"
                try:
                    eng = create_engine(temp_url, connect_args={"check_same_thread": False})
                    with eng.connect():
                        logger.info(f"Using tempdir SQLite database: {temp_url}")
                        return eng
                except Exception:
                    # In-memory SQLite
                    logger.info("Using in-memory SQLite database")
                    return create_engine(
                        "sqlite:///:memory:",
                        connect_args={"check_same_thread": False},
                        poolclass=StaticPool
                    )
        raise

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes database tables."""
    from app.database import models  # Ensure models are imported
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas verified / initialized.")
