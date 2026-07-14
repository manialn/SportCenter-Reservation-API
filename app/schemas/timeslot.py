import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class TimeSlotResponse(BaseModel):
    id: UUID
    facility_id: UUID
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TimeSlotCreateRequest(BaseModel):
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be earlier than end_time")
        return self

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class TimeSlotPublicResponse(BaseModel):
    id: UUID
    facility_id: UUID
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time

    model_config = ConfigDict(from_attributes=True)


class TimeSlotUpdateRequest(BaseModel):
    date: datetime.date | None = None
    start_time: datetime.time | None = None
    end_time: datetime.time | None = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValueError("start_time must be earlier than end_time")
        return self