from fastapi import HTTPException,status
from uuid import UUID
from sqlalchemy import select,func
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Facility,User
from app.enumsfile.enum import FacilityType
from app.core.logger import log_calls, get_logger

logger = get_logger(__name__)

@log_calls
async def get_facilities_service(db: AsyncSession,page: int,
    page_size: int,search: str | None,
    facility_type: FacilityType | None):

    logger.info("Fetching facilities list page=%s page_size=%s search=%s type=%s", page, page_size, search, facility_type)

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

    logger.info("Facilities fetched successfully total_count=%s returned_items=%s", total, len(facilities))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": facilities,
    }

@log_calls
async def get_facility_detail_service(facility_id: UUID,db: AsyncSession,):
    logger.info("Fetching facility detail facility_id=%s", facility_id)

    result = await db.execute(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.is_active.is_(True),
        ))

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning("Facility detail failed not found or inactive facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found")

    logger.info("Facility detail fetched successfully facility_id=%s name=%s", facility_id, facility.name)

    return facility

@log_calls
async def create_facility_service(name: str,description: str | None,
    facility_type: FacilityType,price_per_hour: Decimal,
    db: AsyncSession):
    logger.info("Creating new facility name=%s type=%s", name, facility_type)

    result = await db.execute(
        select(Facility).where(Facility.name == name)
    )
    facility = result.scalar_one_or_none()

    if facility:
        logger.warning("Facility creation failed already exists name=%s", name)
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

    logger.info("Facility created successfully facility_id=%s name=%s", facility.id, name)

    return facility

@log_calls
async def update_facility_service(facility_id: UUID,name: str | None,
    description: str | None,facility_type: FacilityType | None,
    price_per_hour: Decimal | None,db: AsyncSession):
    logger.info("Update facility attempt facility_id=%s", facility_id)

    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning("Facility update failed not found facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found",)

    if name is not None:
        result = await db.execute(
            select(Facility).where(
                Facility.name == name,
                Facility.id != facility_id,
            ))

        if result.scalar_one_or_none():
            logger.warning("Facility update failed name collision facility_id=%s new_name=%s", facility_id, name)
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

    logger.info("Facility updated successfully facility_id=%s", facility_id)

    return facility

@log_calls
async def activate_facility_service(facility_id: UUID,db: AsyncSession,):
    logger.info("Activation attempt facility_id=%s", facility_id)

    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning("Activation failed facility not found facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found")

    if facility.is_active:
        logger.warning("Activation failed already active facility_id=%s", facility_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Facility is already active")

    facility.is_active = True

    await db.commit()
    await db.refresh(facility)

    logger.info("Facility activated successfully facility_id=%s", facility_id)

    return {"message": "Facility activated successfully"}

@log_calls
async def deactivate_facility_service(facility_id: UUID,db: AsyncSession,):
    logger.info("Deactivation attempt facility_id=%s", facility_id)

    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        logger.warning("Deactivation failed facility not found facility_id=%s", facility_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found")

    if not facility.is_active:
        logger.warning("Deactivation failed already inactive facility_id=%s", facility_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Facility is already deactivated")

    facility.is_active = False

    await db.commit()
    await db.refresh(facility)

    logger.info("Facility deactivated successfully facility_id=%s", facility_id)

    return {"message": "Facility deactivated successfully"}

