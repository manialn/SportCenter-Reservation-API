from datetime import time,datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel,field_validator,model_validator,ConfigDict

from app.enumsfile.enum import WeekDay


class FacilityScheduleCreateRequest(BaseModel):
    day_of_week: WeekDay
    open_time: time
    close_time: time
    slot_duration: int
    price_override: Decimal | None = None

    @field_validator("slot_duration")
    @classmethod
    def validate_slot_duration(cls, value: int):
        if value <= 0:
            raise ValueError("slot_duration must be greater than 0.")
        return value

    @field_validator("price_override")
    @classmethod
    def validate_price_override(cls, value: Decimal | None):
        if value is not None and value < 0:
            raise ValueError("price_override cannot be negative.")
        return value

    @model_validator(mode="after")
    def validate_times(self):
        if self.open_time >= self.close_time:
            raise ValueError("open_time must be earlier than close_time.")
        return self
    
class FacilityScheduleResponse(BaseModel):
    id: UUID
    facility_id: UUID
    day_of_week: WeekDay
    open_time: time
    close_time: time
    slot_duration: int
    price_override: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FacilitySchedulePublicResponse(BaseModel):
    day_of_week: WeekDay
    open_time: time
    close_time: time
    slot_duration: int
    price_override: Decimal | None

    model_config = ConfigDict(from_attributes=True)


class FacilityScheduleUpdateRequest(BaseModel):
    day_of_week: WeekDay | None = None
    open_time: time | None = None
    close_time: time | None = None
    slot_duration: int | None = None
    price_override: Decimal | None = None

    @field_validator("slot_duration")
    @classmethod
    def validate_slot_duration(cls, value: int | None):
        if value is not None and value <= 0:
            raise ValueError("slot_duration must be greater than 0.")
        return value

    @field_validator("price_override")
    @classmethod
    def validate_price_override(cls, value: Decimal | None):
        if value is not None and value < 0:
            raise ValueError("price_override cannot be negative.")
        return value

    @model_validator(mode="after")
    def validate_times(self):
        if (
            self.open_time is not None
            and self.close_time is not None
            and self.open_time >= self.close_time
        ):
            raise ValueError("open_time must be earlier than close_time.")
        return self