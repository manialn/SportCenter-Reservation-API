import pytest
from fastapi import status
from app.enumsfile.enum import FacilityType
import uuid


@pytest.mark.asyncio
async def test_get_facilities_success(client, facility_factory):
    await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,)

    response = await client.get("/facilities")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) == 1
    facility = data["items"][0]
    assert facility["name"] == "Football"
    assert facility["facility_type"] == FacilityType.FOOTBALL.value
    assert float(facility["price_per_hour"]) == 100

@pytest.mark.asyncio
async def test_get_facilities_empty_list(client):
    response = await client.get("/facilities")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search",
    [
        "Foot",
        "football",
        "FOOT",
    ],
)
async def test_get_facilities_search(client, facility_factory, search):
    await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,)

    await facility_factory(name="Basketball",
        facility_type=FacilityType.BASKETBALL,price_per_hour=200,)

    response = await client.get(f"/facilities?search={search}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Football"

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "facility_type",
    [
        FacilityType.FOOTBALL,
        FacilityType.BASKETBALL,
        FacilityType.TENNIS,
        FacilityType.VOLLEYBALL,
    ],
)
async def test_get_facilities_filter_by_type(client,facility_factory,
    facility_type,):
    await facility_factory(name="Facility 1",
        facility_type=facility_type,price_per_hour=100,)

    await facility_factory(name="Another Facility",
        facility_type=FacilityType.FOOTBALL
        if facility_type != FacilityType.FOOTBALL
        else FacilityType.BASKETBALL,
        price_per_hour=150,)

    response = await client.get(f"/facilities?facility_type={facility_type.value}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["facility_type"] == facility_type.value

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page,page_size,expected_count",
    [
        (1, 5, 5),
        (2, 5, 5),
        (3, 5, 2),
    ],
)
async def test_get_facilities_pagination(client,facility_factory,
    page,page_size,expected_count,):
    for i in range(12):
        await facility_factory(
            name=f"Facility {i}",
            facility_type=FacilityType.FOOTBALL,
            price_per_hour=100,
        )

    response = await client.get(f"/facilities?page={page}&page_size={page_size}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 12
    assert len(data["items"]) == expected_count

@pytest.mark.asyncio
async def test_get_facilities_returns_only_active_facilities(client,facility_factory,):
    await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,
        is_active=True,)

    await facility_factory(name="Basketball",
        facility_type=FacilityType.BASKETBALL,price_per_hour=200,
        is_active=False,)

    response = await client.get("/facilities")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Football"

@pytest.mark.asyncio
async def test_get_facility_detail_success(client,facility_factory,):
    facility = await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,)

    response = await client.get(f"/facilities/{facility.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(facility.id)
    assert data["name"] == "Football"
    assert data["facility_type"] == FacilityType.FOOTBALL.value
    assert data["price_per_hour"] == "100.00"

@pytest.mark.asyncio
async def test_get_facility_detail_not_found(client):
    response = await client.get(f"/facilities/{uuid.uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()

    assert data["detail"] == "Facility not found"

@pytest.mark.asyncio
async def test_get_facility_detail_inactive_facility(client,facility_factory,):
    facility = await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,
        is_active=False,)

    response = await client.get(f"/facilities/{facility.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()

    assert data["detail"] == "Facility not found"

#create_facility
@pytest.mark.asyncio
async def test_create_facility_success(authorized_admin_client):
    request = {
        "name": "Football",
        "description": "Football field",
        "facility_type": FacilityType.FOOTBALL.value,
        "price_per_hour": "100.00",
    }

    response = await authorized_admin_client.post("/facilities",json=request,)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == request["name"]
    assert data["description"] == request["description"]
    assert data["facility_type"] == request["facility_type"]
    assert data["price_per_hour"] == request["price_per_hour"]

@pytest.mark.asyncio
async def test_create_facility_duplicate_name(authorized_admin_client,facility_factory,):
    await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,)

    request = {
        "name": "Football",
        "description": "Duplicate facility",
        "facility_type": FacilityType.FOOTBALL.value,
        "price_per_hour": "150.00",
    }

    response = await authorized_admin_client.post("/facilities",json=request,)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()

    assert data["detail"] == "Facility already exists"

#update_facility
@pytest.mark.asyncio
async def test_update_facility_success(authorized_admin_client,facility_factory,):
    facility = await facility_factory(name="Football",
        description="Old description",facility_type=FacilityType.FOOTBALL,
        price_per_hour=100,)

    request = {
        "name": "New Football",
        "description": "New description",
        "facility_type": FacilityType.BASKETBALL.value,
        "price_per_hour": "250.00",
    }

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}",json=request,)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(facility.id)
    assert data["name"] == request["name"]
    assert data["description"] == request["description"]
    assert data["facility_type"] == request["facility_type"]
    assert data["price_per_hour"] == request["price_per_hour"]

@pytest.mark.asyncio
async def test_update_facility_not_found(authorized_admin_client,):
    request = {
        "name": "New Football",
        "description": "New description",
        "facility_type": FacilityType.FOOTBALL.value,
        "price_per_hour": "250.00",
    }

    response = await authorized_admin_client.patch(f"/facilities/{uuid.uuid4()}",json=request,)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()

    assert data["detail"] == "Facility not found"

@pytest.mark.asyncio
async def test_update_facility_duplicate_name(authorized_admin_client,facility_factory,):
    await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,)

    facility = await facility_factory(name="Basketball",
        facility_type=FacilityType.BASKETBALL,price_per_hour=150,)

    request = {"name": "Football",}

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}",json=request,)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()

    assert data["detail"] == "Facility already exists"

@pytest.mark.asyncio
async def test_update_facility_partial_update(authorized_admin_client,facility_factory,):
    facility = await facility_factory(name="Football",
        description="Old description",facility_type=FacilityType.FOOTBALL,
        price_per_hour=100,)

    request = {"price_per_hour": "300.00",}

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}",json=request,)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == str(facility.id)
    assert data["name"] == "Football"
    assert data["description"] == "Old description"
    assert data["facility_type"] == FacilityType.FOOTBALL.value
    assert data["price_per_hour"] == "300.00"

#Activate
@pytest.mark.asyncio
async def test_activate_facility_success(authorized_admin_client,facility_factory,db_session):
    facility = await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,
        is_active=False,)

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}/activate",)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["message"] == "Facility activated successfully"

    await db_session.refresh(facility)
    assert facility.is_active is True

@pytest.mark.asyncio
async def test_activate_facility_not_found(authorized_admin_client,):
    response = await authorized_admin_client.patch(f"/facilities/{uuid.uuid4()}/activate",)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()

    assert data["detail"] == "Facility not found"

@pytest.mark.asyncio
async def test_activate_facility_already_active(authorized_admin_client,facility_factory,):
    facility = await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,
        is_active=True,)

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}/activate",)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()

    assert data["detail"] == "Facility is already active"

#DeActive
@pytest.mark.asyncio
async def test_deactivate_facility_success(authorized_admin_client,facility_factory,db_session,):
    facility = await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,
        is_active=True,)

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}/deactivate",)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["message"] == "Facility deactivated successfully"

    await db_session.refresh(facility)
    assert facility.is_active is False

@pytest.mark.asyncio
async def test_deactivate_facility_not_found(authorized_admin_client,):
    response = await authorized_admin_client.patch(f"/facilities/{uuid.uuid4()}/deactivate",)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()

    assert data["detail"] == "Facility not found"

@pytest.mark.asyncio
async def test_deactivate_facility_already_deactivated(authorized_admin_client,facility_factory,):
    facility = await facility_factory(name="Football",
        facility_type=FacilityType.FOOTBALL,price_per_hour=100,
        is_active=False,)

    response = await authorized_admin_client.patch(f"/facilities/{facility.id}/deactivate",)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()

    assert data["detail"] == "Facility is already deactivated"
