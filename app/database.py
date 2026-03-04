import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()
SessionLocal = None
engine = None

try:
    db_url = settings.DATABASE_URL

    # If it's a plain mysql:// URL (no driver specified), force pymysql
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

    # Strip stale SSL query params from URL if any
    if "?" in db_url and db_url.startswith("mysql"):
        db_url = db_url.split("?")[0]

    connect_args = {}
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully.")
except Exception as exc:
    logger.error(
        "Failed to create database engine: %s\n"
        "Set the DATABASE_URL environment variable in Render dashboard.",
        exc,
    )


def get_db():
    if SessionLocal is None:
        raise RuntimeError(
            "Database is not configured. "
            "Please set the DATABASE_URL environment variable."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()