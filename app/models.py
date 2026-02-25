from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base


class LinkPrecedence(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    linked_id = Column(Integer, nullable=True)
    link_precedence = Column(
        Enum(LinkPrecedence), nullable=False, default=LinkPrecedence.primary
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)