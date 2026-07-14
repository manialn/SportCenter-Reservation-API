import pytest
import uuid
from datetime import date, time
from fastapi import status
from app.enumsfile.enum import WeekDay

#create
@pytest.mark.asyncio
async def test_create_timeslot_successfully(authorized_admin_client,
    facility_factory,facility_schedule_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["facility_id"] == str(facility.id)
    assert data["date"] == "2026-07-13"
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "10:00:00"
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_create_timeslot_facility_not_found(authorized_admin_client,):
    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{uuid.uuid4()}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Facility not found."}

@pytest.mark.asyncio
async def test_create_timeslot_facility_inactive(authorized_admin_client,facility_factory,):
    facility = await facility_factory(is_active=False)

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Facility is inactive."}

@pytest.mark.asyncio
async def test_create_timeslot_schedule_not_found(authorized_admin_client,facility_factory,):
    facility = await facility_factory()

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No active schedule found for this day."}

@pytest.mark.asyncio
async def test_create_timeslot_outside_working_hours(authorized_admin_client,facility_factory,
    facility_schedule_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "07:00:00",
            "end_time": "08:00:00",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time slot is outside facility working hours."}

@pytest.mark.asyncio
async def test_create_timeslot_invalid_slot_duration(authorized_admin_client,facility_factory,
    facility_schedule_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "09:30:00",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time slot duration must be 60 minutes."}

@pytest.mark.asyncio
async def test_create_timeslot_duplicate(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Time slot already exists."}

@pytest.mark.asyncio
async def test_create_timeslot_invalid_time_range(authorized_admin_client,facility_factory,
    facility_schedule_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    response = await authorized_admin_client.post(
        f"/timeslots/facilities/{facility.id}",
        json={
            "date": "2026-07-13",
            "start_time": "10:00:00",
            "end_time": "09:00:00",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

#get_timeslot
@pytest.mark.asyncio
async def test_get_timeslots_success(client,facility_factory,timeslot_factory,):
    facility = await facility_factory()

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(10, 0),
        end_time=time(11, 0),
    )

    response = await client.get(
        f"/timeslots/facilities/{facility.id}",
        params={
            "date": "2026-07-13",
            "page": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2

    assert data[0]["start_time"] == "09:00:00"
    assert data[0]["end_time"] == "10:00:00"

    assert data[1]["start_time"] == "10:00:00"
    assert data[1]["end_time"] == "11:00:00"

@pytest.mark.asyncio
async def test_get_timeslots_facility_not_found(client,):
    response = await client.get(
        f"/timeslots/facilities/{uuid.uuid4()}",
        params={
            "date": "2026-07-13",
            "page": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Facility not found."}

@pytest.mark.asyncio
async def test_get_timeslots_not_found(client,facility_factory,):
    facility = await facility_factory()

    response = await client.get(
        f"/timeslots/facilities/{facility.id}",
        params={
            "date": "2026-07-13",
            "page": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No time slots found for this date."}

@pytest.mark.asyncio
async def test_get_timeslots_pagination(client,facility_factory,timeslot_factory,):
    facility = await facility_factory()

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(8, 0),
        end_time=time(9, 0),
    )

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(10, 0),
        end_time=time(11, 0),
    )

    response = await client.get(
        f"/timeslots/facilities/{facility.id}",
        params={
            "date": "2026-07-13",
            "page": 2,
            "page_size": 1,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["start_time"] == "09:00:00"
    assert data[0]["end_time"] == "10:00:00"

@pytest.mark.asyncio
async def test_get_timeslots_only_active(client,facility_factory,timeslot_factory,):
    facility = await facility_factory()

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
        is_active=True,
    )

    await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(10, 0),
        end_time=time(11, 0),
        is_active=False,
    )

    response = await client.get(
        f"/timeslots/facilities/{facility.id}",
        params={
            "date": "2026-07-13",
            "page": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["start_time"] == "09:00:00"
    assert data[0]["end_time"] == "10:00:00"

#update
@pytest.mark.asyncio
async def test_update_timeslot_successfully(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}",
        json={
            "date": "2026-07-13",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(timeslot.id)
    assert data["facility_id"] == str(facility.id)
    assert data["date"] == "2026-07-13"
    assert data["start_time"] == "10:00:00"
    assert data["end_time"] == "11:00:00"

@pytest.mark.asyncio
async def test_update_timeslot_not_found(authorized_admin_client,):
    response = await authorized_admin_client.patch(
        f"/timeslots/{uuid.uuid4()}",
        json={
            "date": "2026-07-13",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Time slot not found."}

@pytest.mark.asyncio
async def test_update_timeslot_only_end_time_invalid_duration(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=120,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(11, 0),
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}",
        json={
            "end_time": "10:00:00"
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time slot duration must be 120 minutes."}

@pytest.mark.asyncio
async def test_update_timeslot_only_date_successfully(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}",
        json={
            "date": "2026-07-20"
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["date"] == "2026-07-20"
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "10:00:00"


@pytest.mark.asyncio
async def test_update_timeslot_duplicate(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    first_timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    second_timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(10, 0),
        end_time=time(11, 0),
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{second_timeslot.id}",
        json={
            "date": "2026-07-13",
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Time slot already exists."}

@pytest.mark.asyncio
async def test_update_timeslot_invalid_time_range(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}",
        json={
            "start_time": "11:00:00",
            "end_time": "10:00:00",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_update_timeslot_invalid_time_range_after_merge(authorized_admin_client,facility_factory,
    facility_schedule_factory,timeslot_factory,):
    facility = await facility_factory()

    await facility_schedule_factory(
        facility_id=facility.id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
    )

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        date=date(2026, 7, 13),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}",
        json={
            "start_time": "10:00:00"
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Start time must be earlier than end time."}

#active
@pytest.mark.asyncio
async def test_activate_timeslot_successfully(authorized_admin_client,facility_factory,
    timeslot_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        is_active=False,
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}/activate"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Time slot activated successfully."}

@pytest.mark.asyncio
async def test_activate_timeslot_not_found(authorized_admin_client,):
    response = await authorized_admin_client.patch(
        f"/timeslots/{uuid.uuid4()}/activate"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Time slot not found."}

@pytest.mark.asyncio
async def test_activate_timeslot_already_active(authorized_admin_client,facility_factory,
    timeslot_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        is_active=True,
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}/activate"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time slot is already active."}

#deactive
@pytest.mark.asyncio
async def test_deactivate_timeslot_successfully(authorized_admin_client,
    facility_factory,timeslot_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        is_active=True,
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}/deactivate"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Time slot deactivated successfully."}

@pytest.mark.asyncio
async def test_deactivate_timeslot_not_found(authorized_admin_client,):
    response = await authorized_admin_client.patch(
        f"/timeslots/{uuid.uuid4()}/deactivate"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Time slot not found."}

@pytest.mark.asyncio
async def test_deactivate_timeslot_already_inactive(authorized_admin_client,
    facility_factory,timeslot_factory,):
    facility = await facility_factory()

    timeslot = await timeslot_factory(
        facility_id=facility.id,
        is_active=False,
    )

    response = await authorized_admin_client.patch(
        f"/timeslots/{timeslot.id}/deactivate"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time slot is already inactive."}