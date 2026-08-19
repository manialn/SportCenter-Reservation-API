import pytest
from app.cache.cache_service import cache_service
from app.cache.cache_keys import CacheKeys


@pytest.mark.asyncio
async def test_cache_set_and_get():
    key = "test:cache:user"
    value = {
        "id": 1,
        "name": "mani",
    }

    await cache_service.set(key, value)

    result = await cache_service.get(key)

    assert result == value

@pytest.mark.asyncio
async def test_cache_delete():
    key = "test:cache:delete"

    await cache_service.set(key, {"value": "test"})

    assert await cache_service.exists(key) is True

    await cache_service.delete(key)

    assert await cache_service.exists(key) is False


#Unit Test

def test_cache_keys():
    assert CacheKeys.facility("123") == "facility:123"

    assert CacheKeys.facilities(
        page=1,
        page_size=10,
        search=None,
        facility_type=None,
    ) == "facilities:1:10:all:all"

    assert CacheKeys.facility_schedule("123") == "facility_schedule:123"

    assert CacheKeys.timeslots(
        facility_id="123",
        date="2026-08-19",
        page=1,
        page_size=10,
    ) == "timeslots:123:2026-08-19:1:10"