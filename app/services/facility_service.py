from fastapi import HTTPException,status
from uuid import UUID
from sqlalchemy import select,func
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Facility
from app.enumsfile.enum import FacilityType
from app.core.logger import log_calls, get_logger
from app.cache.cache_keys import cache_keys
from app.cache.cache_service import cache_service
from fastapi.encoders import jsonable_encoder

logger = get_logger(__name__)

@log_calls
async def get_facilities_service(db: AsyncSession,page: int,
    page_size: int,search: str | None,
    facility_type: FacilityType | None):

    cache_key = cache_keys.facilities(
    page=page,
    page_size=page_size,
    search=search,
    facility_type=facility_type.value if facility_type else None,
    )
    cached_facilities = await cache_service.get(cache_key)
    if cached_facilities is not None:
        return cached_facilities

    query = select(Facility).where(Facility.is_active.is_(True))

    if search:
        query = query.where(
            Facility.name.ilike(f"%{search}%")
        )

    if facility_type:
        query = query.where(
            Facility.facility_type == facility_type
        )

    total_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(total_query)

    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )

    facilities = result.scalars().all()

    response = {
    "total": total,
    "page": page,
    "page_size": page_size,
    "items": jsonable_encoder(facilities),
    }

    await cache_service.set(
        key=cache_key,
        value=response,
        expire=1800,
        )

    return response

@log_calls
async def get_facility_detail_service(facility_id: UUID,db: AsyncSession,):

    cache_key = cache_keys.facility(str(facility_id))
    cached_facility = await cache_service.get(cache_key)
    if cached_facility is not None:
        return cached_facility

    result = await db.execute(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.is_active.is_(True),
        ))

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning(
            "BUSINESS facility_not_found facility_id=%s",
            facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found")
    
    facility_data = jsonable_encoder(facility)

    await cache_service.set(
        key=cache_key,
        value=facility_data,
        expire=1800,
    )

    return facility_data

@log_calls
async def create_facility_service(name: str,description: str | None,
    facility_type: FacilityType,price_per_hour: Decimal,
    db: AsyncSession):

    result = await db.execute(
        select(Facility).where(Facility.name == name)
    )
    facility = result.scalar_one_or_none()

    if facility:
        logger.warning(
            "BUSINESS facility_already_exists name=%s",
            name,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Facility already exists",)

    facility = Facility(
        name=name,
        description=description,
        facility_type=facility_type,
        price_per_hour=price_per_hour,
    )

    db.add(facility)
    await db.commit()
    await db.refresh(facility)

    await cache_service.delete_pattern("facilities:*")

    logger.info(
        "BUSINESS facility_created facility_id=%s name=%s type=%s price_per_hour=%s",
        facility.id,
        facility.name,
        facility.facility_type,
        facility.price_per_hour,
    )

    return facility

@log_calls
async def update_facility_service(facility_id: UUID,name: str | None,
    description: str | None,facility_type: FacilityType | None,
    price_per_hour: Decimal | None,db: AsyncSession):

    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning(
            "BUSINESS facility_not_found facility_id=%s",
            facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found",)

    if name is not None:
        result = await db.execute(
            select(Facility).where(
                Facility.name == name,
                Facility.id != facility_id,
            ))

        if result.scalar_one_or_none():
            logger.warning(
                "BUSINESS duplicate_facility_name facility_id=%s new_name=%s",
                facility_id,
                name,
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Facility already exists",)

        facility.name = name

    if description is not None:
        facility.description = description

    if facility_type is not None:
        facility.facility_type = facility_type

    if price_per_hour is not None:
        facility.price_per_hour = price_per_hour

    await db.commit()
    await db.refresh(facility)

    await cache_service.delete(cache_keys.facility(str(facility.id)))
    await cache_service.delete_pattern("facilities:*")

    logger.info(
        "BUSINESS facility_updated facility_id=%s",
        facility.id,
    )

    return facility

@log_calls
async def activate_facility_service(facility_id: UUID,db: AsyncSession,):

    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning(
            "BUSINESS facility_not_found facility_id=%s",
            facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found")

    if facility.is_active:
        logger.warning(
            "BUSINESS facility_already_active facility_id=%s",
            facility_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Facility is already active")

    facility.is_active = True

    await db.commit()
    await db.refresh(facility)

    await cache_service.delete(cache_keys.facility(str(facility.id)))
    await cache_service.delete_pattern("facilities:*")

    logger.info(
        "BUSINESS facility_activated facility_id=%s",
        facility.id,
    )

    return {"message": "Facility activated successfully"}

@log_calls
async def deactivate_facility_service(facility_id: UUID,db: AsyncSession,):

    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning(
            "BUSINESS facility_not_found facility_id=%s",
            facility_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found")

    if not facility.is_active:
        logger.warning(
            "BUSINESS facility_already_deactivated facility_id=%s",
            facility_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Facility is already deactivated")

    facility.is_active = False

    await db.commit()
    await db.refresh(facility)

    await cache_service.delete(cache_keys.facility(str(facility.id)))
    await cache_service.delete_pattern("facilities:*")

    logger.info(
        "BUSINESS facility_deactivated facility_id=%s",
        facility.id,
    )

    return {"message": "Facility deactivated successfully"}