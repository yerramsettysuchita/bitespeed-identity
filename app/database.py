from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Strip any extra query params so we can cleanly inspect the URL
db_url = settings.DATABASE_URL

# Determine the right connect_args based on the dialect
if db_url.startswith("postgresql"):
    # For Render's internal PostgreSQL, SSL is handled via the URL itself.
    # No extra connect_args needed.
    connect_args = {}
else:
    # For MySQL / PyMySQL — strip query params and disable forced SSL
    # (local dev; production should use PostgreSQL on Render)
    db_url = db_url.split("?")[0]
    connect_args = {}

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()