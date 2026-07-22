from fastapi import HTTPException,status
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time
from decimal import Decimal
from app.models import Facility, FacilitySchedule
from app.enumsfile.enum import WeekDay
from app.cache.cache_service import cache_service
from app.cache.cache_keys import CacheKeys
from fastapi.encoders import jsonable_encoder
from app.core.logger import get_logger,log_calls

logger = get_logger(__name__)

@log_calls
async def create_schedule_service(facility_id: UUID,day_of_week: WeekDay,
    open_time: time,close_time: time,
    slot_duration: int,price_override: Decimal | None,
    db: AsyncSession,):

    logger.info(
        "Creating facility schedule. facility_id=%s day=%s",
        facility_id,
        day_of_week.value,
    )

    facility = await db.scalar(
        select(Facility).where(Facility.id == facility_id))

    if facility is None:
        logger.warning(
            "Facility not found. facility_id=%s",
            facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found.")

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.facility_id == facility_id,
            FacilitySchedule.day_of_week == day_of_week,
        )
    )

    if schedule:
        logger.warning(
            "Schedule already exists for day. facility_id=%s day=%s existing_schedule_id=%s",
            facility_id,
            day_of_week.value,
            schedule.id,
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Schedule for this day already exists.")

    new_schedule = FacilitySchedule(
        facility_id=facility_id,
        day_of_week=day_of_week,
        open_time=open_time,
        close_time=close_time,
        slot_duration=slot_duration,
        price_override=price_override,
    )

    logger.debug(
        "Persisting new schedule. facility_id=%s day=%s",
        facility_id,
        day_of_week.value,
    )

    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)

    await cache_service.delete(
    CacheKeys.facility_schedule(str(facility_id)))

    logger.debug(
        "Schedule persisted. schedule_id=%s active=%s",
        new_schedule.id,
        new_schedule.is_active,
    )

    logger.info(
        "Schedule created successfully. schedule_id=%s facility_id=%s",
        new_schedule.id,
        facility_id,
    )

    return new_schedule

@log_calls
async def get_schedule_service(facility_id: UUID,db: AsyncSession):

    cache_key = CacheKeys.facility_schedule(str(facility_id))
    cached_data = await cache_service.get(cache_key)
    if cached_data is not None:
        logger.info(
        "Schedules returned from cache. facility_id=%s",
        facility_id,
        )
        return cached_data

    logger.info(
        "Fetching facility schedules. facility_id=%s",
        facility_id,
    )

    facility = await db.scalar(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.is_active == True,
        )
    )

    if facility is None:
        logger.warning(
            "Facility not found. facility_id=%s",
            facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found.")
    
    schedules = await db.scalars(
        select(FacilitySchedule)
        .where(
            FacilitySchedule.facility_id == facility_id,
            FacilitySchedule.is_active == True,
        )
        .order_by(FacilitySchedule.day_of_week)
    )

    schedules_list = schedules.all()

    logger.info(
        "Schedules fetched successfully. facility_id=%s count=%s",
        facility_id,
        len(schedules_list),
    )
    response = jsonable_encoder(schedules_list)

    await cache_service.set(
    cache_key,
    response,
)

    return response

@log_calls
async def update_schedule_service(schedule_id: UUID,day_of_week: WeekDay | None,
    open_time: time | None,close_time: time | None,
    slot_duration: int | None,price_override: Decimal | None,
    db: AsyncSession):

    logger.info(
        "Updating facility schedule. schedule_id=%s",
        schedule_id,
    )

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.id == schedule_id
        )
    )

    if schedule is None:
        logger.warning(
            "Schedule not found. schedule_id=%s",
            schedule_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Schedule not found.")

    logger.debug(
        "Current schedule state. schedule_id=%s day=%s open=%s close=%s duration=%s price=%s active=%s",
        schedule.id,
        schedule.day_of_week.value,
        schedule.open_time,
        schedule.close_time,
        schedule.slot_duration,
        schedule.price_override,
        schedule.is_active,
    )

    if day_of_week is not None:
        existing_schedule = await db.scalar(
            select(FacilitySchedule).where(
                FacilitySchedule.facility_id == schedule.facility_id,
                FacilitySchedule.day_of_week == day_of_week,
                FacilitySchedule.id != schedule.id
            )
        )

        if existing_schedule:
            logger.warning(
                "Schedule update rejected because another schedule already exists. schedule_id=%s facility_id=%s day=%s existing_schedule_id=%s",
                schedule.id,
                schedule.facility_id,
                day_of_week.value,
                existing_schedule.id,
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Schedule for this day already exists.")

    if day_of_week is not None:
        schedule.day_of_week = day_of_week
    if open_time is not None:
        schedule.open_time = open_time
    if close_time is not None:
        schedule.close_time = close_time
    if slot_duration is not None:
        schedule.slot_duration = slot_duration
    if price_override is not None:
        schedule.price_override = price_override

    if schedule.open_time >= schedule.close_time:
        logger.warning(
            "Invalid schedule time range. schedule_id=%s open_time=%s close_time=%s",
            schedule.id,
            schedule.open_time,
            schedule.close_time,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="open_time must be earlier than close_time.")

    logger.debug(
        "Persisting schedule updates. schedule_id=%s",
        schedule.id,
    )

    await db.commit()
    await db.refresh(schedule)

    await cache_service.delete(
    CacheKeys.facility_schedule(str(schedule.facility_id)))

    logger.debug(
        "Updated schedule state. schedule_id=%s day=%s open=%s close=%s duration=%s price=%s active=%s",
        schedule.id,
        schedule.day_of_week.value,
        schedule.open_time,
        schedule.close_time,
        schedule.slot_duration,
        schedule.price_override,
        schedule.is_active,
    )

    logger.info(
        "Schedule updated successfully. schedule_id=%s facility_id=%s",
        schedule.id,
        schedule.facility_id,
    )

    return schedule


@log_calls
async def activate_schedule_service(schedule_id: UUID,db: AsyncSession):

    logger.info(
        "Activating schedule. schedule_id=%s",
        schedule_id,
    )

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.id == schedule_id
        )
    )

    if schedule is None:
        logger.warning(
            "Schedule not found. schedule_id=%s",
            schedule_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Schedule not found.")

    if schedule.is_active:
        logger.warning(
            "Schedule is already active. schedule_id=%s",
            schedule_id,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Schedule is already active.")

    logger.debug(
        "Persisting schedule activation. schedule_id=%s",
        schedule.id,
    )

    schedule.is_active = True

    await db.commit()
    await db.refresh(schedule)

    await cache_service.delete(
    CacheKeys.facility_schedule(str(schedule.facility_id)))

    logger.info(
        "Schedule activated successfully. schedule_id=%s facility_id=%s",
        schedule.id,
        schedule.facility_id,
    )

    return {"message": "Schedule activated successfully."}


@log_calls
async def deactivate_schedule_service(schedule_id: UUID,db: AsyncSession):

    logger.info(
        "Deactivating schedule. schedule_id=%s",
        schedule_id,
    )

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.id == schedule_id
        )
    )

    if schedule is None:
        logger.warning(
            "Schedule not found. schedule_id=%s",
            schedule_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Schedule not found.")

    if not schedule.is_active:
        logger.warning(
            "Schedule is already inactive. schedule_id=%s",
            schedule_id,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Schedule is already inactive.")

    logger.debug(
        "Persisting schedule deactivation. schedule_id=%s",
        schedule.id,
    )

    schedule.is_active = False

    await db.commit()
    await db.refresh(schedule)

    await cache_service.delete(
    CacheKeys.facility_schedule(str(schedule.facility_id)))

    logger.info(
        "Schedule deactivated successfully. schedule_id=%s facility_id=%s",
        schedule.id,
        schedule.facility_id,
    )

    return {"message": "Schedule deactivated successfully."}