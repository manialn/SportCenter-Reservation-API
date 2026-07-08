from pydantic import BaseModel,ConfigDict,Field
from uuid import UUID
from decimal import Decimal
from app.enumsfile.enum import FacilityType

class FacilityResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    facility_type: FacilityType
    price_per_hour: Decimal

    model_config = ConfigDict(from_attributes=True)

class FacilityListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FacilityResponse]

class FacilityCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    facility_type: FacilityType
    price_per_hour: Decimal = Field(gt=0)

class FacilityUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    facility_type: FacilityType | None = None
    price_per_hour: Decimal | None = Field(default=None, gt=0)