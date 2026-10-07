from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from . import models


def generate_slots(windows, day: date, slot_minutes: int):
    """
    windows: list of (start_time, end_time) tuples for that day
    Returns every slot that fully fits inside a window.
    """
    step = timedelta(minutes=slot_minutes)
    slots = set()

    for start_t, end_t in windows:
        current = datetime.combine(day, start_t)
        end = datetime.combine(day, end_t)
        while current + step <= end:
            slots.add(current)
            current += step

    return sorted(slots)


def get_free_slots(db: Session, user: models.User, day: date):
    windows = [
        (a.start_time, a.end_time)
        for a in user.availability
        if a.weekday == day.weekday()
    ]
    all_slots = generate_slots(windows, day, user.slot_minutes)

    day_start = datetime.combine(day, time.min)
    day_end = day_start + timedelta(days=1)

    booked_rows = (
        db.query(models.Booking.start_at)
        .filter(
            models.Booking.user_id == user.id,
            models.Booking.status == "confirmed",
            models.Booking.start_at >= day_start,
            models.Booking.start_at < day_end,
        )
        .all()
    )
    booked = {row[0] for row in booked_rows}

    now = datetime.now()
    return [s for s in all_slots if s not in booked and s > now]