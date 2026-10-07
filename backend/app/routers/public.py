from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..slots import get_free_slots

router = APIRouter(prefix="/public", tags=["public"])


def find_owner(db: Session, slug: str) -> models.User:
    user = db.query(models.User).filter(models.User.slug == slug.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Page not found")
    return user


@router.get("/{slug}")
def owner_info(slug: str, db: Session = Depends(get_db)):
    user = find_owner(db, slug)
    return {
        "name": user.name,
        "slug": user.slug,
        "slot_minutes": user.slot_minutes,
    }


@router.get("/{slug}/slots")
def free_slots(slug: str, day: date, db: Session = Depends(get_db)):
    user = find_owner(db, slug)
    return [s.isoformat() for s in get_free_slots(db, user, day)]


@router.post("/{slug}/book", response_model=schemas.BookingOut)
def book(slug: str, data: schemas.BookingCreate, db: Session = Depends(get_db)):
    user = find_owner(db, slug)

    start = data.start_at.replace(tzinfo=None)

    if start not in get_free_slots(db, user, start.date()):
        raise HTTPException(status_code=409, detail="This slot is not available")

    booking = models.Booking(
        user_id=user.id,
        guest_name=data.guest_name,
        guest_email=data.guest_email.lower(),
        start_at=start,
        end_at=start + timedelta(minutes=user.slot_minutes),
    )
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Someone just booked this slot")

    db.refresh(booking)
    return booking