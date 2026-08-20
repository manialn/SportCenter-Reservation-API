from fastapi import APIRouter,status,Query
from datetime import date
from uuid import UUID
from app.core.dependency import db_dependency,admin_dependency
from app.schemas.timeslot import TimeSlotResponse,TimeSlotCreateRequest,TimeSlotPublicResponse,TimeSlotUpdateRequest
from app.schemas.error import ErrorResponse
from app.services.timeslot_service import (
create_timeslot_service,get_timeslots_service,update_timeslot_service,active_timeslot_service,deactive_timeslot_service
)

router = APIRouter(
    prefix="/timeslots"
)

@router.post("/facilities/{facility_id}",status_code=status.HTTP_201_CREATED,response_model=TimeSlotResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Facility is inactive or invalid time slot"},
        404: {"model": ErrorResponse, "description": "Facility or schedule not found"},
        409: {"model": ErrorResponse, "description": "Time slot already exists"},
    },)
async def create_timeslot(facility_id: UUID,request: TimeSlotCreateRequest,admin: admin_dependency,db: db_dependency):
    return await create_timeslot_service(facility_id=facility_id,date=request.date,
        start_time=request.start_time,end_time=request.end_time,
        db=db)

@router.get("/facilities/{facility_id}",status_code=status.HTTP_200_OK,response_model=list[TimeSlotPublicResponse],
    responses={
        404: {"model": ErrorResponse, "description": "Facility or time slots not found"},
    },)
async def get_timeslots(facility_id: UUID,date: date,db: db_dependency,
    page: int = Query(1, ge=1),page_size: int = Query(10, ge=1, le=100)):
    return await get_timeslots_service(facility_id=facility_id,date=date,
        page=page,page_size=page_size,db=db)

@router.patch("/{timeslot_id}",status_code=status.HTTP_200_OK,response_model=TimeSlotResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid time range or slot duration"},
        404: {"model": ErrorResponse, "description": "Time slot, facility, or schedule not found"},
        409: {"model": ErrorResponse, "description": "Time slot already exists"},
    },)
async def update_timeslot(timeslot_id: UUID,request: TimeSlotUpdateRequest,admin: admin_dependency,db: db_dependency):
    return await update_timeslot_service(timeslot_id=timeslot_id,date=request.date,
        start_time=request.start_time,end_time=request.end_time,
        db=db)

@router.patch("/{timeslot_id}/activate",status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Time slot is already active"},
        404: {"model": ErrorResponse, "description": "Time slot not found"},
    },)
async def active_timeslot(timeslot_id: UUID,admin: admin_dependency,db: db_dependency):
    return await active_timeslot_service(timeslot_id=timeslot_id,db=db)

@router.patch("/{timeslot_id}/deactivate",status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Time slot is already inactive"},
        404: {"model": ErrorResponse, "description": "Time slot not found"},
    },)
async def deactive_timeslot(timeslot_id: UUID,admin: admin_dependency,db: db_dependency):
    return await deactive_timeslot_service(timeslot_id=timeslot_id,db=db)