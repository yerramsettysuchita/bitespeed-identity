from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class IdentifyRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None

    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

    @field_validator("phoneNumber")
    @classmethod
    def clean_phone(cls, v):
        if v is not None:
            return str(v).strip() or None
        return v


class ContactResponse(BaseModel):
    primaryContatctId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]


class IdentifyResponse(BaseModel):
    contact: ContactResponse


class ContactSchema(BaseModel):
    id: int
    phone_number: Optional[str]
    email: Optional[str]
    linked_id: Optional[int]
    link_precedence: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True