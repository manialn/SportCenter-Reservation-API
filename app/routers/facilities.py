from fastapi import APIRouter,status,Query
from uuid import UUID
from typing import Optional
from app.core.dependency import db_dependency,user_dependency,admin_dependency
from app.schemas.facility import FacilityListResponse,FacilityResponse,FacilityCreateRequest,FacilityUpdateRequest
from app.services.facility_services import (
get_facilities_service,get_facility_detail_service,create_facility_service,update_facility_service
,activate_facility_service,deactivate_facility_service)
from app.enumsfile.enum import FacilityType

router = APIRouter(
    prefix="/facilities"
)

@router.get("",status_code=status.HTTP_200_OK,response_model=FacilityListResponse)
async def get_facilities(db: db_dependency,page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),search: Optional[str] = None,
    facility_type: Optional[FacilityType] = None
):
    return await get_facilities_service(db=db,page=page,
        page_size=page_size,search=search,
        facility_type=facility_type,)

@router.get("/{facility_id}",status_code=status.HTTP_200_OK,response_model=FacilityResponse)
async def get_facility_detail(facility_id: UUID,db: db_dependency,):
    return await get_facility_detail_service(
        facility_id=facility_id,db=db)

@router.post("",status_code=status.HTTP_201_CREATED,response_model=FacilityResponse)
async def create_facilities(request: FacilityCreateRequest,admin: admin_dependency,db: db_dependency):
    return await create_facility_service(name=request.name,description=request.description,
        facility_type=request.facility_type,
        price_per_hour=request.price_per_hour,db=db)
    
@router.patch("/{facility_id}",status_code=status.HTTP_200_OK,response_model=FacilityResponse)
async def update_facility(facility_id: UUID,request: FacilityUpdateRequest,admin: admin_dependency,db: db_dependency):
    return await update_facility_service(facility_id=facility_id,name=request.name,
        description=request.description,facility_type=request.facility_type,
        price_per_hour=request.price_per_hour,db=db)

@router.patch("/{facility_id}/activate",status_code=status.HTTP_200_OK)
async def activate_facility(facility_id: UUID,admin: admin_dependency,db: db_dependency):
    return await activate_facility_service(facility_id=facility_id,db=db)

@router.patch("/{facility_id}/deactivate",status_code=status.HTTP_200_OK)
async def deactivate_facility(facility_id: UUID,admin: admin_dependency,db: db_dependency):
    return await deactivate_facility_service(facility_id=facility_id,db=db)