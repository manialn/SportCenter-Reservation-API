from datetime import date, time, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.enumsfile.enum import BookingStatus,FacilityType,PaymentStatus


class BookingCreateRequest(BaseModel):
    timeslot_id: UUID


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    timeslot_id: UUID
    booking_status: BookingStatus
    total_price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingListResponse(BaseModel):
    id: UUID
    facility_name: str
    facility_type: FacilityType
    date: date
    start_time: time
    end_time: time
    booking_status: BookingStatus
    total_price: Decimal

class BookingDetailResponse(BaseModel):
    id: UUID
    booking_status: BookingStatus
    total_price: Decimal

    facility_name: str
    facility_type: FacilityType

    date: date
    start_time: time
    end_time: time

    payment_status: PaymentStatus | None = None
    transaction_id: str | None = None

    created_at: datetime
    updated_at: datetime

class BookingAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    phone_number: str

    facility_name: str
    facility_type: FacilityType

    date: date
    start_time: time
    end_time: time

    payment_status: PaymentStatus | None = None

    booking_status: BookingStatus
    total_price: Decimal