from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import IdentifyRequest, IdentifyResponse, ContactSchema
from app.service import reconcile
from app.models import Contact

router = APIRouter()


@router.post(
    "/identify",
    response_model=IdentifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Identify & reconcile a contact",
)
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):
    if not payload.email and not payload.phoneNumber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of email or phoneNumber must be provided.",
        )
    result = reconcile(db, email=payload.email, phone_number=payload.phoneNumber)
    return IdentifyResponse(contact=result)


@router.get(
    "/contacts",
    response_model=List[ContactSchema],
    summary="List all contacts",
)
def list_contacts(db: Session = Depends(get_db)):
    return (
        db.query(Contact)
        .filter(Contact.deleted_at.is_(None))  # type: ignore
        .order_by(Contact.id)  # type: ignore
        .all()
    )


@router.delete("/contacts/reset", summary="Reset all contacts")
def reset_contacts(db: Session = Depends(get_db)):
    db.query(Contact).delete()
    db.commit()
    return {"message": "All contacts deleted successfully."}