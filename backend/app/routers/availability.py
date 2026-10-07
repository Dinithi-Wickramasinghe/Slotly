from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("", response_model=List[schemas.AvailabilityOut])
def list_availability(user: models.User = Depends(get_current_user)):
    return sorted(user.availability, key=lambda a: (a.weekday, a.start_time))


@router.post("", response_model=schemas.AvailabilityOut)
def add_availability(
    data: schemas.AvailabilityIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not 0 <= data.weekday <= 6:
        raise HTTPException(status_code=400, detail="weekday must be 0 to 6")
    if data.start_time >= data.end_time:
        raise HTTPException(status_code=400, detail="Start must be before end")

    for a in user.availability:
        if (
            a.weekday == data.weekday
            and data.start_time < a.end_time
            and a.start_time < data.end_time
        ):
            raise HTTPException(
                status_code=400, detail="This overlaps an existing time window"
            )

    item = models.Availability(user_id=user.id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_availability(
    item_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    item = db.get(models.Availability, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}