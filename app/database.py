import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Aiven MySQL requires SSL - using correct pymysql SSL format
connect_args = {}
if "aivencloud" in settings.DATABASE_URL:
    connect_args = {
        "ssl": {
            "ca": "/etc/ssl/certs/ca-certificates.crt"
        }
    }

engine = create_engine(
    settings.DATABASE_URL,
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