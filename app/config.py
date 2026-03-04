from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # On Render: set DATABASE_URL in the Environment Variables dashboard.
    # Format for PostgreSQL (Render free DB):
    #   postgresql://user:password@host/dbname
    # Format for MySQL (local dev):
    #   mysql+pymysql://root:password@localhost:3306/bitespeed
    DATABASE_URL: str = "postgresql://localhost/bitespeed"
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()