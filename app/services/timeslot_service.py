from datetime import datetime,time,date
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.enumsfile.enum import WeekDay
from app.models import Facility, FacilitySchedule, TimeSlot
from app.cache.cache_service import cache_service
from app.cache.cache_keys import CacheKeys
from fastapi.encoders import jsonable_encoder
from app.core.logger import get_logger, log_calls

logger = get_logger(__name__)


@log_calls
async def create_timeslot_service(facility_id: UUID,date: date,
    start_time: time,end_time: time,
    db: AsyncSession,):
    facility = await db.scalar(
        select(Facility).where(Facility.id == facility_id)
    )

    if not facility:
        logger.warning("Facility not found. facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found.",)

    if not facility.is_active:
        logger.warning("Inactive facility. facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Facility is inactive.",)

    weekday = WeekDay(date.strftime("%A").lower())

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.facility_id == facility_id,
            FacilitySchedule.day_of_week == weekday,
            FacilitySchedule.is_active == True,
        )
    )

    if not schedule:
        logger.warning(
            "No active schedule. facility_id=%s weekday=%s",
            facility_id,
            weekday.value,
        )
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,detail="No active schedule found for this day.",)

    if (
        start_time < schedule.open_time
        or end_time > schedule.close_time
    ):
        logger.warning(
            "Outside working hours. facility_id=%s date=%s",
            facility_id,
            date,
        )
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,detail="Time slot is outside facility working hours.",)

    start_dt = datetime.combine(date, start_time)
    end_dt = datetime.combine(date, end_time)

    duration = int((end_dt - start_dt).total_seconds() / 60)

    if duration != schedule.slot_duration:
        logger.warning(
            "Invalid slot duration. facility_id=%s expected=%s actual=%s",
            facility_id,
            schedule.slot_duration,
            duration,
        )
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,detail=f"Time slot duration must be {schedule.slot_duration} minutes.",)

    existing = await db.scalar(
        select(TimeSlot).where(
            TimeSlot.facility_id == facility_id,
            TimeSlot.date == date,
            TimeSlot.start_time == start_time,
            TimeSlot.end_time == end_time,
        )
    )

    if existing:
        logger.warning(
            "Duplicate time slot. facility_id=%s date=%s start=%s end=%s",
            facility_id,
            date,
            start_time,
            end_time,
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Time slot already exists.",)

    timeslot = TimeSlot(
        facility_id=facility_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
    )

    db.add(timeslot)

    await db.commit()
    await db.refresh(timeslot)

    await cache_service.delete_pattern(
    f"timeslots:{facility_id}:{date}:*")

    logger.info(
        "Time slot created. id=%s facility_id=%s date=%s start=%s end=%s",
        timeslot.id,
        facility_id,
        date,
        start_time,
        end_time,
    )

    return timeslot

@log_calls
async def get_timeslots_service(facility_id: UUID,date: date,
    page: int,page_size: int,
    db: AsyncSession,):

    cache_key = CacheKeys.timeslots(
        str(facility_id),
        str(date),
        page,
        page_size,)
    cached_timeslots = await cache_service.get(cache_key)
    if cached_timeslots is not None:
        return cached_timeslots

    facility = await db.scalar(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.is_active == True,
        )
    )

    if not facility:
        logger.warning("Facility not found. facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found.",)

    offset = (page - 1) * page_size

    result = await db.scalars(
        select(TimeSlot)
        .where(
            TimeSlot.facility_id == facility_id,
            TimeSlot.date == date,
            TimeSlot.is_active == True,
        )
        .order_by(TimeSlot.start_time)
        .offset(offset)
        .limit(page_size)
    )

    timeslots = result.all()

    if not timeslots:
        logger.warning(
            "No active time slots found. facility_id=%s date=%s",
            facility_id,
            date,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No time slots found for this date.",)

    logger.info(
        "Returned %d time slots. facility_id=%s date=%s page=%d page_size=%d",
        len(timeslots),
        facility_id,
        date,
        page,
        page_size,
    )
    response = jsonable_encoder(timeslots)

    await cache_service.set(
        cache_key,
        response,
        expire=60,
    )

    return response

@log_calls
async def update_timeslot_service(timeslot_id: UUID,date: date | None,
    start_time: time | None,end_time: time | None,
    db: AsyncSession,):
    timeslot = await db.scalar(
        select(TimeSlot).where(TimeSlot.id == timeslot_id)
    )

    if not timeslot:
        logger.warning("Time slot not found. timeslot_id=%s", timeslot_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Time slot not found.",)

    new_date = date if date is not None else timeslot.date
    new_start_time = start_time if start_time is not None else timeslot.start_time
    new_end_time = end_time if end_time is not None else timeslot.end_time

    if new_start_time >= new_end_time:
        logger.warning(
            "Invalid time range. timeslot_id=%s start=%s end=%s",
            timeslot_id,
            new_start_time,
            new_end_time,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Start time must be earlier than end time.",)

    facility = await db.scalar(
        select(Facility).where(
            Facility.id == timeslot.facility_id,
            Facility.is_active == True,
        )
    )

    if not facility:
        logger.warning(
            "Facility not found. facility_id=%s",
            timeslot.facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found.",)

    weekday = WeekDay(new_date.strftime("%A").lower())

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.facility_id == facility.id,
            FacilitySchedule.day_of_week == weekday,
            FacilitySchedule.is_active == True,
        )
    )

    if not schedule:
        logger.warning(
            "Facility schedule not found. facility_id=%s weekday=%s",
            facility.id,
            weekday.value,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility schedule not found.",)

    start_dt = datetime.combine(new_date, new_start_time)
    end_dt = datetime.combine(new_date, new_end_time)

    duration = int((end_dt - start_dt).total_seconds() / 60)

    if duration != schedule.slot_duration:
        logger.warning(
            "Invalid slot duration. timeslot_id=%s expected=%s actual=%s",
            timeslot_id,
            schedule.slot_duration,
            duration,
        )
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,detail=f"Time slot duration must be {schedule.slot_duration} minutes.",)

    existing = await db.scalar(
        select(TimeSlot).where(
            TimeSlot.facility_id == facility.id,
            TimeSlot.date == new_date,
            TimeSlot.start_time == new_start_time,
            TimeSlot.end_time == new_end_time,
            TimeSlot.id != timeslot.id,
        )
    )

    if existing:
        logger.warning(
            "Duplicate time slot. facility_id=%s date=%s start=%s end=%s",
            facility.id,
            new_date,
            new_start_time,
            new_end_time,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot already exists.",
        )

    timeslot.date = new_date
    timeslot.start_time = new_start_time
    timeslot.end_time = new_end_time

    await db.commit()
    await db.refresh(timeslot)

    await cache_service.delete_pattern(
    f"timeslots:{timeslot.facility_id}:{new_date}:*")

    logger.info(
        "Time slot updated. id=%s facility_id=%s",
        timeslot.id,
        facility.id,
    )

    return timeslot

@log_calls
async def active_timeslot_service(timeslot_id: UUID,db: AsyncSession,):
    timeslot = await db.scalar(
        select(TimeSlot).where(TimeSlot.id == timeslot_id)
    )

    if not timeslot:
        logger.warning(
            "Time slot not found. timeslot_id=%s",
            timeslot_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Time slot not found.",)

    if timeslot.is_active:
        logger.warning(
            "Time slot already active. timeslot_id=%s",
            timeslot_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Time slot is already active.",)

    timeslot.is_active = True

    await db.commit()
    await db.refresh(timeslot)

    await cache_service.delete_pattern(
    f"timeslots:{timeslot.facility_id}:{timeslot.date}:*")

    logger.info(
        "Time slot activated. id=%s facility_id=%s",
        timeslot.id,
        timeslot.facility_id,
    )

    return {"message": "Time slot activated successfully."}

@log_calls
async def deactive_timeslot_service(timeslot_id: UUID,db: AsyncSession,):
    timeslot = await db.scalar(
        select(TimeSlot).where(TimeSlot.id == timeslot_id)
    )

    if not timeslot:
        logger.warning(
            "Time slot not found. timeslot_id=%s",
            timeslot_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Time slot not found.",)

    if not timeslot.is_active:
        logger.warning(
            "Time slot already inactive. timeslot_id=%s",
            timeslot_id,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Time slot is already inactive.",)

    timeslot.is_active = False

    await db.commit()
    await db.refresh(timeslot)

    await cache_service.delete_pattern(
    f"timeslots:{timeslot.facility_id}:{timeslot.date}:*")

    logger.info(
        "Time slot deactivated. id=%s facility_id=%s",
        timeslot.id,
        timeslot.facility_id,
    )

    return {"message": "Time slot deactivated successfully."}

