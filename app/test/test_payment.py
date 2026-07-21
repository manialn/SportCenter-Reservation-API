import uuid
import pytest
from fastapi import status
from app.enumsfile.enum import BookingStatus, PaymentStatus
from app.models import Payment
from app.enumsfile.enum import PaymentStatus
from app.gateways.mock_payment_gateway import MockPaymentGateway
from uuid import UUID
from decimal import Decimal

@pytest.mark.asyncio
async def test_create_payment_success(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,db_session,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        booking_status=BookingStatus.PENDING,
        total_price=250,
    )

    response = await authorized_client.post(
        f"/payments/{booking.id}"
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    payment = await db_session.get(Payment, uuid.UUID(data["id"]))

    assert payment is not None
    assert payment.booking_id == booking.id
    assert payment.amount == booking.total_price
    assert payment.payment_status == PaymentStatus.SUCCESS

    await db_session.refresh(booking)

    assert booking.booking_status == BookingStatus.CONFIRMED

@pytest.mark.asyncio
async def test_create_payment_booking_not_found(authorized_client,):
    response = await authorized_client.post(
        f"/payments/{uuid.uuid4()}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Booking not found."}

@pytest.mark.asyncio
async def test_create_payment_booking_already_confirmed(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        booking_status=BookingStatus.CONFIRMED,
    )

    response = await authorized_client.post(
        f"/payments/{booking.id}"
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == {"detail": "Only pending bookings can be paid."}

@pytest.mark.asyncio
async def test_create_payment_booking_already_cancelled(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        booking_status=BookingStatus.CANCELLED,
    )

    response = await authorized_client.post(
        f"/payments/{booking.id}"
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == {"detail": "Only pending bookings can be paid."}

@pytest.mark.asyncio
async def test_create_payment_already_exists(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,payment_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        booking_status=BookingStatus.PENDING,
    )

    await payment_factory(
        booking_id=booking.id,
        amount=booking.total_price,
    )

    response = await authorized_client.post(
        f"/payments/{booking.id}"
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == {"detail": "Payment already exists for this booking."}

@pytest.mark.asyncio
async def test_create_payment_booking_belongs_to_another_user(authorized_client,user_factory,
    facility_factory,timeslot_factory,
    booking_factory,):
    another_user = await user_factory()

    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=another_user.id,
        timeslot_id=timeslot.id,
    )

    response = await authorized_client.post(
        f"/payments/{booking.id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Booking not found."}

@pytest.mark.asyncio
async def test_mock_payment_gateway_returns_success():
    gateway = MockPaymentGateway()

    transaction_id, payment_status = await gateway.create_payment(
        amount=Decimal("100")
    )

    assert UUID(transaction_id)
    assert payment_status == PaymentStatus.SUCCESS

@pytest.mark.asyncio
async def test_get_payment_success(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,payment_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
    )

    payment = await payment_factory(
        booking_id=booking.id,
        amount=booking.total_price,
    )

    response = await authorized_client.get(
        f"/payments/{payment.id}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(payment.id)
    assert float(data["amount"]) == float(payment.amount)
    assert data["payment_status"] == payment.payment_status.value
    assert data["payment_method"] == payment.payment_method.value

@pytest.mark.asyncio
async def test_get_payment_not_found(authorized_client,):
    response = await authorized_client.get(
        f"/payments/{uuid.uuid4()}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Payment not found."}

@pytest.mark.asyncio
async def test_get_payment_belongs_to_another_user(authorized_client,user_factory,
    facility_factory,timeslot_factory,
    booking_factory,payment_factory,):
    another_user = await user_factory()

    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=another_user.id,
        timeslot_id=timeslot.id,
    )

    payment = await payment_factory(
        booking_id=booking.id,
        amount=booking.total_price,
    )

    response = await authorized_client.get(
        f"/payments/{payment.id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Payment not found."}