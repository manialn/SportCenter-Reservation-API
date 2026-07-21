from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.enumsfile.enum import BookingStatus, PaymentStatus
from app.gateways.mock_payment_gateway import MockPaymentGateway
from app.gateways.payment_gateway import PaymentGateway
from app.models import Booking, Payment
from app.core.logger import get_logger, log_calls


logger = get_logger(__name__)


@log_calls
async def create_payment_service(booking_id: UUID,user_id: UUID,
    db: AsyncSession,gateway: PaymentGateway | None = None,):

    logger.info(
        "Payment creation requested booking_id=%s user_id=%s",
        booking_id,
        user_id,
    )

    gateway = gateway or MockPaymentGateway()

    booking = await db.scalar(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
    )

    if not booking:
        logger.warning(
            "Payment creation rejected: booking not found "
            "booking_id=%s user_id=%s",
            booking_id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Booking not found.",)

    if booking.booking_status != BookingStatus.PENDING:
        logger.warning(
            "Payment creation rejected: invalid booking status "
            "booking_id=%s user_id=%s status=%s",
            booking_id,
            user_id,
            booking.booking_status,
        )

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Only pending bookings can be paid.",)

    existing_payment = await db.scalar(
        select(Payment).where(
            Payment.booking_id == booking.id,
        )
    )

    if existing_payment:
        logger.warning(
            "Payment creation rejected: payment already exists "
            "booking_id=%s payment_id=%s user_id=%s",
            booking.id,
            existing_payment.id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Payment already exists for this booking.",)

    transaction_id, payment_status = await gateway.create_payment(
        amount=booking.total_price,
    )

    logger.info(
        "Payment gateway response booking_id=%s "
        "transaction_id=%s payment_status=%s",
        booking.id,
        transaction_id,
        payment_status,
    )

    payment = Payment(
        booking_id=booking.id,
        amount=booking.total_price,
        payment_status=payment_status,
        transaction_id=transaction_id,
    )

    db.add(payment)

    if payment_status == PaymentStatus.SUCCESS:
        booking.booking_status = BookingStatus.CONFIRMED

        logger.info(
            "Booking confirmed after successful payment "
            "booking_id=%s transaction_id=%s",
            booking.id,
            transaction_id,
        )

    await db.commit()
    await db.refresh(payment)

    logger.info(
        "Payment created successfully payment_id=%s booking_id=%s "
        "user_id=%s payment_status=%s amount=%s",
        payment.id,
        booking.id,
        user_id,
        payment.payment_status,
        payment.amount,
    )

    return payment


@log_calls
async def get_payment_service(payment_id: UUID,user_id: UUID,
    db: AsyncSession,):

    logger.info(
        "Payment detail requested payment_id=%s user_id=%s",
        payment_id,
        user_id,
    )

    payment = await db.scalar(
        select(Payment)
        .join(
            Booking,
            Payment.booking_id == Booking.id,
        )
        .where(
            Payment.id == payment_id,
            Booking.user_id == user_id,
        )
    )

    if payment is None:
        logger.warning(
            "Payment detail request rejected: payment not found "
            "payment_id=%s user_id=%s",
            payment_id,
            user_id,
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Payment not found.",)

    logger.info(
        "Payment detail retrieved successfully payment_id=%s user_id=%s",
        payment.id,
        user_id,
    )

    return payment