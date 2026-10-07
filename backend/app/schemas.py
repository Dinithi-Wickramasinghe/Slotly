from datetime import time, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    slug: str = Field(pattern=r"^[a-z0-9-]{3,50}$")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    slug: str
    slot_minutes: int


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AvailabilityIn(BaseModel):
    weekday: int
    start_time: time
    end_time: time


class AvailabilityOut(AvailabilityIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class BookingCreate(BaseModel):
    guest_name: str = Field(min_length=1, max_length=100)
    guest_email: EmailStr
    start_at: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_name: str
    guest_email: EmailStr
    start_at: datetime
    end_at: datetime
    status: str