from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models import TimeSlot,Booking,Facility,FacilitySchedule,Payment,User
from app.enumsfile.enum import BookingStatus, WeekDay
from app.core.logger import get_logger, log_calls


logger = get_logger(__name__)


@log_calls
async def create_booking_service(user_id: UUID,timeslot_id: UUID,
    db: AsyncSession,):
    logger.info(
        "Booking creation requested user_id=%s timeslot_id=%s",
        user_id,
        timeslot_id,
    )

    timeslot = await db.scalar(
        select(TimeSlot).where(
            TimeSlot.id == timeslot_id,
            TimeSlot.is_active == True,
        )
    )

    if not timeslot:
        logger.warning(
            "Booking creation rejected: active timeslot not found "
            "timeslot_id=%s user_id=%s",
            timeslot_id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Time slot not found.",)

    existing_booking = await db.scalar(
        select(Booking).where(
            Booking.timeslot_id == timeslot_id,
        )
    )

    if existing_booking:
        logger.warning(
            "Booking creation rejected: timeslot already booked "
            "timeslot_id=%s existing_booking_id=%s user_id=%s",
            timeslot_id,
            existing_booking.id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Time slot is already booked.",)

    facility = await db.scalar(
        select(Facility).where(
            Facility.id == timeslot.facility_id,
            Facility.is_active == True,
        )
    )

    if not facility:
        logger.warning(
            "Booking creation rejected: active facility not found "
            "facility_id=%s timeslot_id=%s user_id=%s",
            timeslot.facility_id,
            timeslot_id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Facility not found.",)

    weekday = WeekDay(timeslot.date.strftime("%A").lower())

    schedule = await db.scalar(
        select(FacilitySchedule).where(
            FacilitySchedule.facility_id == facility.id,
            FacilitySchedule.day_of_week == weekday,
            FacilitySchedule.is_active == True,
        )
    )

    if not schedule:
        logger.warning(
            "Booking creation rejected: active schedule not found "
            "facility_id=%s weekday=%s user_id=%s",
            facility.id,
            weekday,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No active schedule found for this day.",)

    total_price = (
        schedule.price_override
        if schedule.price_override is not None
        else facility.price_per_hour
    )

    booking = Booking(
        user_id=user_id,
        timeslot_id=timeslot_id,
        total_price=total_price,
        booking_status=BookingStatus.PENDING,
    )

    db.add(booking)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        logger.warning(
        "Booking creation failed due to duplicate timeslot. "
        "timeslot_id=%s user_id=%s",
        timeslot_id,
        user_id,
    )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,detail="Time slot is already booked.")
    await db.refresh(booking)

    logger.info(
        "Booking created successfully booking_id=%s user_id=%s "
        "timeslot_id=%s facility_id=%s booking_status=%s total_price=%s",
        booking.id,
        user_id,
        timeslot_id,
        facility.id,
        booking.booking_status,
        booking.total_price,
    )

    return booking


@log_calls
async def get_bookings_service(user_id: UUID,page: int,
    page_size: int,db: AsyncSession,):
    offset = (page - 1) * page_size

    logger.info(
        "User bookings requested user_id=%s page=%s page_size=%s",
        user_id,
        page,
        page_size,
    )

    result = await db.execute(
        select(
            Booking.id,
            Facility.name.label("facility_name"),
            Facility.facility_type,
            TimeSlot.date,
            TimeSlot.start_time,
            TimeSlot.end_time,
            Booking.booking_status,
            Booking.total_price,
        )
        .join(TimeSlot, Booking.timeslot_id == TimeSlot.id)
        .join(Facility, TimeSlot.facility_id == Facility.id)
        .where(
            Booking.user_id == user_id,
        )
        .order_by(
            Booking.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    bookings = result.mappings().all()

    logger.info(
        "User bookings retrieved user_id=%s page=%s count=%s",
        user_id,
        page,
        len(bookings),
    )

    return bookings

@log_calls
async def cancel_booking_service(booking_id: UUID,user_id: UUID,
    db: AsyncSession,):
    logger.info(
        "Booking cancellation requested booking_id=%s user_id=%s",
        booking_id,
        user_id,
    )

    booking = await db.scalar(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
    )

    if not booking:
        logger.warning(
            "Booking cancellation rejected: booking not found "
            "booking_id=%s user_id=%s",
            booking_id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking not found.",)

    if booking.booking_status == BookingStatus.CANCELLED:
        logger.warning(
            "Booking cancellation rejected: already cancelled "
            "booking_id=%s user_id=%s",
            booking_id,
            user_id,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is already cancelled.",
        )

    if booking.booking_status != BookingStatus.PENDING:
        logger.warning(
            "Booking cancellation rejected: invalid booking status "
            "booking_id=%s user_id=%s status=%s",
            booking_id,
            user_id,
            booking.booking_status,
        )

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Only pending bookings can be cancelled.",)

    booking.booking_status = BookingStatus.CANCELLED

    await db.commit()
    await db.refresh(booking)

    logger.info(
        "Booking cancelled successfully booking_id=%s user_id=%s",
        booking_id,
        user_id,
    )

    return booking


@log_calls
async def get_bookings_admin_service(page: int,page_size: int,db: AsyncSession,):
    offset = (page - 1) * page_size

    logger.info(
        "Admin bookings requested page=%s page_size=%s",
        page,
        page_size,
    )

    result = await db.execute(
        select(
            Booking.id,
            Booking.user_id,
            User.username,
            User.phone_number,
            Facility.name.label("facility_name"),
            Facility.facility_type,
            TimeSlot.date,
            TimeSlot.start_time,
            TimeSlot.end_time,
            Booking.booking_status,
            Booking.total_price,
            Payment.payment_status,
        )
        .join(User, Booking.user_id == User.id)
        .join(TimeSlot, Booking.timeslot_id == TimeSlot.id)
        .join(Facility, TimeSlot.facility_id == Facility.id)
        .outerjoin(Payment, Payment.booking_id == Booking.id)
        .order_by(
            Booking.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    bookings = result.mappings().all()

    logger.info(
        "Admin bookings retrieved page=%s count=%s",
        page,
        len(bookings),
    )

    return bookings


@log_calls
async def get_booking_detail_service(booking_id: UUID,user_id: UUID,
    db: AsyncSession,):
    logger.info(
        "Booking detail requested booking_id=%s user_id=%s",
        booking_id,
        user_id,
    )

    result = await db.execute(
        select(
            Booking.id,
            Booking.booking_status,
            Booking.total_price,
            Facility.name.label("facility_name"),
            Facility.facility_type,
            TimeSlot.date,
            TimeSlot.start_time,
            TimeSlot.end_time,
            Payment.payment_status,
            Payment.transaction_id,
            Booking.created_at,
            Booking.updated_at,
        )
        .join(
            TimeSlot,
            Booking.timeslot_id == TimeSlot.id,
        )
        .join(
            Facility,
            TimeSlot.facility_id == Facility.id,
        )
        .outerjoin(
            Payment,
            Payment.booking_id == Booking.id,
        )
        .where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
    )

    booking = result.mappings().one_or_none()

    if booking is None:
        logger.warning(
            "Booking detail request rejected: booking not found "
            "booking_id=%s user_id=%s",
            booking_id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking not found.",)

    logger.info(
        "Booking detail retrieved successfully booking_id=%s user_id=%s",
        booking_id,
        user_id,
    )

    return booking