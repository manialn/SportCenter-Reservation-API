from fastapi import APIRouter,status
from uuid import UUID
from app.core.dependency import db_dependency,admin_dependency
from app.schemas.facility_schedule import (
FacilityScheduleResponse,FacilityScheduleCreateRequest,FacilitySchedulePublicResponse,FacilityScheduleUpdateRequest)
from app.schemas.error import ErrorResponse
from app.services.facility_schedule_service import (
create_schedule_service,get_schedule_service,update_schedule_service,
activate_schedule_service,deactivate_schedule_service)

router = APIRouter(
    prefix="/schedule"
)

@router.post("/facilities/{facility_id}",status_code=status.HTTP_201_CREATED,response_model=FacilityScheduleResponse,
    responses={
        404: {"model": ErrorResponse,"description": "Facility not found",},
        409: {"model": ErrorResponse,"description": "Schedule for this day already exists",},
    },)
async def create_schedule(facility_id: UUID,request: FacilityScheduleCreateRequest,admin: admin_dependency,db: db_dependency):
    return await create_schedule_service(facility_id=facility_id,day_of_week=request.day_of_week,
        open_time=request.open_time,close_time=request.close_time,
        slot_duration=request.slot_duration,price_override=request.price_override,
        db=db)

@router.get("/facilities/{facility_id}",status_code=status.HTTP_200_OK,response_model=list[FacilitySchedulePublicResponse],
    responses={
        404: {"model": ErrorResponse,"description": "Facility not found",},
    },)
async def get_schedule(facility_id: UUID,db: db_dependency):
    return await get_schedule_service(facility_id=facility_id,db=db)

@router.patch("/{schedule_id}",status_code=status.HTTP_200_OK,response_model=FacilityScheduleResponse,
    responses={
        400: {"model": ErrorResponse,"description": "open_time must be earlier than close_time",},
        404: {"model": ErrorResponse,"description": "Schedule not found",},
        409: {"model": ErrorResponse,"description": "Schedule for this day already exists",},
    },)
async def update_schedule(schedule_id: UUID,request: FacilityScheduleUpdateRequest,admin: admin_dependency,db: db_dependency):
    return await update_schedule_service(schedule_id=schedule_id,day_of_week=request.day_of_week,
        open_time=request.open_time,close_time=request.close_time,
        slot_duration=request.slot_duration,price_override=request.price_override,
        db=db)

@router.patch("/{schedule_id}/activate",status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse,"description": "Schedule is already active",},
        404: {"model": ErrorResponse,"description": "Schedule not found",},
    },)
async def activate_schedule(schedule_id: UUID,admin: admin_dependency,db: db_dependency):
    return await activate_schedule_service(schedule_id=schedule_id,db=db)

@router.patch("/{schedule_id}/deactivate",status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse,"description": "Schedule is already inactive",},
        404: {"model": ErrorResponse,"description": "Schedule not found",},
    },)
async def deactivate_schedule(schedule_id: UUID,admin: admin_dependency,db: db_dependency):
    return await deactivate_schedule_service(schedule_id=schedule_id,db=db)