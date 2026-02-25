from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from typing import Optional

from app.models import Contact, LinkPrecedence
from app.schemas import ContactResponse


def _get_root_primary(db: Session, contact: Contact) -> Contact:
    """Walk up linkedId chain to find the true primary."""
    if contact.link_precedence == LinkPrecedence.primary:  # type: ignore
        return contact
    parent = db.query(Contact).filter(Contact.id == contact.linked_id).first()  # type: ignore
    if parent:
        return _get_root_primary(db, parent)
    return contact


def _get_full_cluster(db: Session, primary_id: int) -> list:
    """Return primary + all its secondaries."""
    primary = db.query(Contact).filter(Contact.id == primary_id).first()  # type: ignore
    secondaries = (
        db.query(Contact)
        .filter(and_(Contact.linked_id == primary_id, Contact.deleted_at.is_(None)))  # type: ignore
        .all()
    )
    return [primary] + secondaries if primary else secondaries


def _build_response(db: Session, primary_id: int) -> ContactResponse:
    """Build the consolidated contact response from the cluster."""
    cluster = _get_full_cluster(db, primary_id)
    primary = next((c for c in cluster if c.link_precedence == LinkPrecedence.primary), None)

    emails, phones, secondary_ids = [], [], []

    if primary:
        if primary.email:        emails.append(primary.email)
        if primary.phone_number: phones.append(primary.phone_number)

    for c in cluster:
        if c.link_precedence == LinkPrecedence.secondary:
            secondary_ids.append(c.id)
            if c.email and c.email not in emails:
                emails.append(c.email)
            if c.phone_number and c.phone_number not in phones:
                phones.append(c.phone_number)

    return ContactResponse(
        primaryContatctId=primary_id,
        emails=emails,
        phoneNumbers=phones,
        secondaryContactIds=secondary_ids,
    )


def reconcile(db: Session, email: Optional[str], phone_number: Optional[str]) -> ContactResponse:
    """
    Core identity reconciliation logic.

    Case 1 → No match:          Create new primary contact
    Case 2 → Match + new info:  Create secondary contact linked to primary
    Case 3 → Two primaries:     Demote newer primary, merge clusters
    Case 4 → Exact match:       Return existing cluster unchanged
    """
    now = datetime.utcnow()

    # Build query conditions
    conditions = []
    if email:        conditions.append(Contact.email == email)
    if phone_number: conditions.append(Contact.phone_number == phone_number)

    matched = (
        db.query(Contact)
        .filter(or_(*conditions), Contact.deleted_at.is_(None))  # type: ignore
        .order_by(Contact.created_at.asc())  # type: ignore
        .all()
    )

    # ── CASE 1: No existing contacts ──────────────────────────────────────────
    if not matched:
        new_contact = Contact(
            email=email,
            phone_number=phone_number,
            linked_id=None,
            link_precedence=LinkPrecedence.primary,
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return _build_response(db, new_contact.id)  # type: ignore

    # Resolve each matched contact to its root primary
    primaries = []
    for c in matched:
        root = _get_root_primary(db, c)
        if root not in primaries:
            primaries.append(root)
    primaries.sort(key=lambda c: c.created_at)
    true_primary = primaries[0]

    # ── CASE 3: Multiple primaries → merge ────────────────────────────────────
    if len(primaries) > 1:
        for demoted in primaries[1:]:
            demoted.link_precedence = LinkPrecedence.secondary  # type: ignore
            demoted.linked_id = true_primary.id  # type: ignore
            demoted.updated_at = datetime.utcnow()  # type: ignore
            # Re-link orphaned secondaries to true primary
            for orphan in db.query(Contact).filter(
                Contact.linked_id == demoted.id, Contact.deleted_at.is_(None)  # type: ignore
            ).all():
                orphan.linked_id = true_primary.id  # type: ignore
                orphan.updated_at = datetime.utcnow()  # type: ignore
        db.commit()

    # ── CASE 2: New info → create secondary ───────────────────────────────────
    cluster = _get_full_cluster(db, true_primary.id)
    existing_emails  = {c.email for c in cluster if c.email}
    existing_phones  = {c.phone_number for c in cluster if c.phone_number}

    has_new = (email and email not in existing_emails) or \
              (phone_number and phone_number not in existing_phones)

    if has_new:
        db.add(Contact(
            email=email,
            phone_number=phone_number,
            linked_id=true_primary.id,
            link_precedence=LinkPrecedence.secondary,
        ))
        db.commit()

    # ── CASE 4: No new info → return existing ─────────────────────────────────
    return _build_response(db, true_primary.id)