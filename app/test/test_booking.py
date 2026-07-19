import pytest
import uuid
from datetime import date as dt_date, time as dt_time
from app.enumsfile.enum import BookingStatus, WeekDay, PaymentMethod, FacilityType, PaymentStatus
from app.models import Payment
from fastapi import status

#create_booking
@pytest.mark.asyncio
async def test_create_booking_success(authorized_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory(
        price_per_hour=100,
    )
    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        price_override=None,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=dt_date(2026, 7, 13),
        start_time=dt_time(9, 0),
        end_time=dt_time(10, 0),
    )

    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(timeslot.id),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["timeslot_id"] == str(timeslot.id)
    assert data["booking_status"] == BookingStatus.PENDING.value
    assert float(data["total_price"]) == 100

@pytest.mark.asyncio
async def test_create_booking_timeslot_not_found(authorized_client,):
    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Time slot not found."}

@pytest.mark.asyncio
async def test_create_booking_inactive_timeslot(authorized_client,facility_factory,
    timeslot_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        is_active=False,
    )

    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(timeslot.id),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Time slot not found."}

@pytest.mark.asyncio
async def test_create_booking_timeslot_already_booked(authorized_client,facility_factory,
    facility_schedule_factory,timeslot_factory,
    booking_factory,test_user,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
    )

    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(timeslot.id),
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == {"detail": "Time slot is already booked."}

@pytest.mark.asyncio
async def test_create_booking_inactive_facility(authorized_client,facility_factory,
    timeslot_factory,):
    facility = await facility_factory(
        is_active=False,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(timeslot.id),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Facility not found."}

@pytest.mark.asyncio
async def test_create_booking_no_active_schedule(authorized_client,facility_factory,
    timeslot_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(timeslot.id),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "No active schedule found for this day."}

@pytest.mark.asyncio
async def test_create_booking_uses_price_override(authorized_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory(
        price_per_hour=100,
    )

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        price_override=150,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    response = await authorized_client.post(
        "/bookings",
        json={
            "timeslot_id": str(timeslot.id),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert float(data["total_price"]) == 150

#get_booking
@pytest.mark.asyncio
async def test_get_bookings_success(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
    )

    response = await authorized_client.get("/bookings")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["facility_name"] == facility.name
    assert data[0]["facility_type"] == facility.facility_type.value
    assert data[0]["date"] == str(timeslot.date)
    assert data[0]["start_time"] == str(timeslot.start_time)
    assert data[0]["end_time"] == str(timeslot.end_time)
    assert data[0]["booking_status"] == booking.booking_status.value
    assert float(data[0]["total_price"]) == float(booking.total_price)

@pytest.mark.asyncio
async def test_get_bookings_empty(authorized_client,):
    response = await authorized_client.get("/bookings")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []

@pytest.mark.asyncio
async def test_get_bookings_does_not_return_other_user_bookings(authorized_client,user_factory,
    facility_factory,timeslot_factory,
    booking_factory,):
    other_user = await user_factory()

    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    await booking_factory(
        user_id=other_user.id,
        timeslot_id=timeslot.id,
    )

    response = await authorized_client.get("/bookings")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []

@pytest.mark.asyncio
async def test_get_bookings_pagination(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    first_timeslot = await timeslot_factory(
        facility_id=facility.id,
        start_time=dt_time(9, 0),
        end_time=dt_time(10, 0),
    )

    second_timeslot = await timeslot_factory(
        facility_id=facility.id,
        start_time=dt_time(10, 0),
        end_time=dt_time(11, 0),
    )

    await booking_factory(
        user_id=test_user.id,
        timeslot_id=first_timeslot.id,
    )

    await booking_factory(
        user_id=test_user.id,
        timeslot_id=second_timeslot.id,
    )

    response = await authorized_client.get(
        "/bookings?page=1&page_size=1"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1

@pytest.mark.asyncio
async def test_get_bookings_ordered_by_latest(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    first_timeslot = await timeslot_factory(
        facility_id=facility.id,
        start_time=dt_time(9, 0),
        end_time=dt_time(10, 0),
    )

    second_timeslot = await timeslot_factory(
        facility_id=facility.id,
        start_time=dt_time(10, 0),
        end_time=dt_time(11, 0),
    )

    first_booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=first_timeslot.id,
    )

    second_booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=second_timeslot.id,
    )

    response = await authorized_client.get("/bookings")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2

    assert data[0]["id"] == str(second_booking.id)
    assert data[1]["id"] == str(first_booking.id)

@pytest.mark.asyncio
async def test_get_booking_detail_success(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,db_session,):
    facility = await facility_factory(
        facility_type=FacilityType.FOOTBALL,
        price_per_hour=100,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=dt_date(2026, 7, 13),
        start_time=dt_time(9, 0),
        end_time=dt_time(10, 0),
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        total_price=100,
    )

    payment = Payment(
        booking_id=booking.id,
        amount=100,
        payment_status=PaymentStatus.SUCCESS,
        payment_method=PaymentMethod.MOCK_GATEWAY,
    )

    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    response = await authorized_client.get(
        f"/bookings/{booking.id}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(booking.id)
    assert data["booking_status"] == booking.booking_status.value
    assert float(data["total_price"]) == 100

    assert data["facility_name"] == facility.name
    assert data["facility_type"] == facility.facility_type.value

    assert data["date"] == str(timeslot.date)
    assert data["start_time"] == str(timeslot.start_time)
    assert data["end_time"] == str(timeslot.end_time)

    assert data["payment_status"] == payment.payment_status.value
    assert data["transaction_id"] == payment.transaction_id

    assert data["created_at"] is not None
    assert data["updated_at"] is not None

@pytest.mark.asyncio
async def test_get_booking_detail_not_found(authorized_client,):
    response = await authorized_client.get(
        f"/bookings/{uuid.uuid4()}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Booking not found."}

@pytest.mark.asyncio
async def test_get_booking_detail_other_user_booking(authorized_client,user_factory,
    facility_factory,timeslot_factory,
    booking_factory,):
    other_user = await user_factory()

    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=other_user.id,
        timeslot_id=timeslot.id,
    )

    response = await authorized_client.get(
        f"/bookings/{booking.id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Booking not found."}

@pytest.mark.asyncio
async def test_get_booking_detail_without_payment(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
    )

    response = await authorized_client.get(
        f"/bookings/{booking.id}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["payment_status"] is None
    assert data["transaction_id"] is None

#cancel_bookings
@pytest.mark.asyncio
async def test_cancel_booking_success(authorized_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        booking_status=BookingStatus.PENDING,
    )

    response = await authorized_client.patch(
        f"/bookings/{booking.id}/cancel"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(booking.id)
    assert data["booking_status"] == BookingStatus.CANCELLED.value

@pytest.mark.asyncio
async def test_cancel_booking_not_found(authorized_client,):
    response = await authorized_client.patch(
        f"/bookings/{uuid.uuid4()}/cancel"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Booking not found."}

@pytest.mark.asyncio
async def test_cancel_booking_already_cancelled(authorized_client,test_user,
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

    response = await authorized_client.patch(
        f"/bookings/{booking.id}/cancel"
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == {"detail": "Booking is already cancelled."}

@pytest.mark.asyncio
async def test_cancel_booking_confirmed_booking(authorized_client,test_user,
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

    response = await authorized_client.patch(
        f"/bookings/{booking.id}/cancel"
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == {"detail": "Only pending bookings can be cancelled."}

#admin_booking
@pytest.mark.asyncio
async def test_get_bookings_admin_success(authorized_admin_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory(
        facility_type=FacilityType.FOOTBALL,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
    )

    booking = await booking_factory(
        user_id=test_user.id,
        timeslot_id=timeslot.id,
        booking_status=BookingStatus.PENDING,
        total_price=100,
    )

    response = await authorized_admin_client.get(
        "/bookings/admin"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == str(booking.id)
    assert data[0]["user_id"] == str(test_user.id)
    assert data[0]["username"] == test_user.username
    assert data[0]["phone_number"] == test_user.phone_number

    assert data[0]["facility_name"] == facility.name
    assert data[0]["facility_type"] == facility.facility_type.value

    assert data[0]["date"] == str(timeslot.date)
    assert data[0]["start_time"] == str(timeslot.start_time)
    assert data[0]["end_time"] == str(timeslot.end_time)

    assert data[0]["booking_status"] == booking.booking_status.value
    assert float(data[0]["total_price"]) == 100

@pytest.mark.asyncio
async def test_get_bookings_admin_forbidden_for_regular_user(authorized_client,):
    response = await authorized_client.get(
        "/bookings/admin"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_get_bookings_admin_empty(authorized_admin_client,):
    response = await authorized_admin_client.get(
        "/bookings/admin"
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []

@pytest.mark.asyncio
async def test_get_bookings_admin_pagination(authorized_admin_client,test_user,
    facility_factory,timeslot_factory,
    booking_factory,):
    facility = await facility_factory()

    first_timeslot = await timeslot_factory(
        facility_id=facility.id,
        start_time=dt_time(9, 0),
        end_time=dt_time(10, 0),
    )

    second_timeslot = await timeslot_factory(
        facility_id=facility.id,
        start_time=dt_time(10, 0),
        end_time=dt_time(11, 0),
    )

    await booking_factory(
        user_id=test_user.id,
        timeslot_id=first_timeslot.id,
    )

    await booking_factory(
        user_id=test_user.id,
        timeslot_id=second_timeslot.id,
    )

    response = await authorized_admin_client.get(
        "/bookings/admin?page=1&page_size=1"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1