import pytest
import uuid
from fastapi import status
from app.enumsfile.enum import WeekDay
from datetime import time

pytestmark = pytest.mark.asyncio


#create_schedule
async def test_create_schedule_success(authorized_admin_client,facility_factory,):
    facility = await facility_factory()

    response = await authorized_admin_client.post(
        f"/schedule/facilities/{facility.id}",
        json={
            "day_of_week": "monday",
            "open_time": "08:00:00",
            "close_time": "22:00:00",
            "slot_duration": 60,
            "price_override": 150,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["facility_id"] == str(facility.id)
    assert data["day_of_week"] == "monday"
    assert data["open_time"] == "08:00:00"
    assert data["close_time"] == "22:00:00"
    assert data["slot_duration"] == 60
    assert data["price_override"] == "150.00"
    assert data["is_active"] is True

async def test_create_schedule_facility_not_found(authorized_admin_client,):
    response = await authorized_admin_client.post(
        f"/schedule/facilities/{uuid.uuid4()}",
        json={
            "day_of_week": "monday",
            "open_time": "08:00:00",
            "close_time": "22:00:00",
            "slot_duration": 60,
            "price_override": 150,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Facility not found."

async def test_create_schedule_duplicate_day(authorized_admin_client,facility_factory,
    facility_schedule_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
    )

    response = await authorized_admin_client.post(
        f"/schedule/facilities/{facility.id}",
        json={
            "day_of_week": "monday",
            "open_time": "09:00:00",
            "close_time": "21:00:00",
            "slot_duration": 60,
            "price_override": 150,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Schedule for this day already exists."

async def test_create_schedule_unauthorized(client,facility_factory,):
    facility = await facility_factory()

    response = await client.post(
        f"/schedule/facilities/{facility.id}",
        json={
            "day_of_week": "monday",
            "open_time": "08:00:00",
            "close_time": "22:00:00",
            "slot_duration": 60,
            "price_override": 150,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_create_schedule_forbidden(authorized_client,facility_factory,):
    facility = await facility_factory()

    response = await authorized_client.post(
        f"/schedule/facilities/{facility.id}",
        json={
            "day_of_week": "monday",
            "open_time": "08:00:00",
            "close_time": "22:00:00",
            "slot_duration": 60,
            "price_override": 150,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_create_schedule_invalid_time(authorized_admin_client,facility_factory):
    facility = await facility_factory()

    response = await authorized_admin_client.post(
        f"/schedule/facilities/{facility.id}",
        json={
            "day_of_week": "monday",
            "open_time": "22:00:00",
            "close_time": "08:00:00",
            "slot_duration": 60,
            "price_override": 150,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

#get_schedule
async def test_get_schedule_success(client,facility_factory,facility_schedule_factory):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
    )

    response = await client.get(f"/schedule/facilities/{facility.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["day_of_week"] == "monday"
    assert data[0]["open_time"] == "08:00:00"
    assert data[0]["close_time"] == "22:00:00"
    assert data[0]["slot_duration"] == 60
    assert data[0]["price_override"] is None

async def test_get_schedule_facility_not_found(client):
    response = await client.get(f"/schedule/facilities/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Facility not found."

async def test_get_schedule_empty_list(client,facility_factory,):
    facility = await facility_factory()

    response = await client.get(f"/schedule/facilities/{facility.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

async def test_get_schedule_excludes_inactive_schedule(client,facility_factory,facility_schedule_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        is_active=False,
    )

    response = await client.get(f"/schedule/facilities/{facility.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

#update_schedule
async def test_update_schedule_success(authorized_admin_client,facility_factory,facility_schedule_factory):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}",
        json={
            "open_time": "09:00:00",
            "price_override": 200,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(schedule.id)
    assert data["facility_id"] == str(facility.id)
    assert data["open_time"] == "09:00:00"
    assert data["close_time"] == "22:00:00"
    assert data["price_override"] == "200.00"

async def test_update_schedule_duplicate_day(authorized_admin_client,facility_factory,facility_schedule_factory):
    facility = await facility_factory()

    schedule1 = await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
    )

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.TUESDAY,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule1.id}",
        json={
            "day_of_week": "tuesday",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Schedule for this day already exists."


async def test_update_schedule_invalid_time(authorized_admin_client,facility_factory,facility_schedule_factory,):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
        open_time=time(8, 0),
        close_time=time(22, 0),
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}",
        json={
            "open_time": "23:00:00",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "open_time must be earlier than close_time."}

async def test_update_schedule_not_found(authorized_admin_client):
    response = await authorized_admin_client.patch(
        f"/schedule/{uuid.uuid4()}",
        json={
            "open_time": "09:00:00",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Schedule not found."

async def test_update_schedule_invalid_slot_duration(authorized_admin_client,facility_factory,facility_schedule_factory):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}",
        json={
            "slot_duration": 0,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

#activate
async def test_activate_schedule_success(authorized_admin_client,facility_factory,facility_schedule_factory):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
        is_active=False,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}/activate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Schedule activated successfully."}

async def test_activate_schedule_not_found(authorized_admin_client):
    response = await authorized_admin_client.patch(
        f"/schedule/{uuid.uuid4()}/activate"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Schedule not found."

async def test_activate_schedule_already_active(authorized_admin_client,facility_factory,facility_schedule_factory,):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
        is_active=True,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}/activate")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Schedule is already active."

#deactive
async def test_deactivate_schedule_success(authorized_admin_client,facility_factory,facility_schedule_factory):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
        is_active=True,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}/deactivate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Schedule deactivated successfully."}

async def test_deactivate_schedule_not_found(authorized_admin_client):
    response = await authorized_admin_client.patch(
        f"/schedule/{uuid.uuid4()}/deactivate"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Schedule not found."

async def test_deactivate_schedule_already_inactive(authorized_admin_client,facility_factory,facility_schedule_factory,):
    facility = await facility_factory()

    schedule = await facility_schedule_factory(
        facility_id=facility.id,
        is_active=False,
    )

    response = await authorized_admin_client.patch(f"/schedule/{schedule.id}/deactivate")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Schedule is already inactive."