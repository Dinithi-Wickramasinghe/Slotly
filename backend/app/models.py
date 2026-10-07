from datetime import datetime
from sqlalchemy import (Column, Integer, String, Time, DateTime,
                        ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    slot_minutes = Column(Integer, default=30)

    availability = relationship("Availability", back_populates="user",
                                cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weekday = Column(Integer, nullable=False)  # 0 = Monday ... 6 = Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    user = relationship("User", back_populates="availability")


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("user_id", "start_at", name="uq_user_slot"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guest_name = Column(String(100), nullable=False)
    guest_email = Column(String(255), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="confirmed")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="bookings")