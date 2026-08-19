import pytest
from fastapi import HTTPException, status
from starlette.requests import Request
from app.limiter.rate_limiter import RedisRateLimiter


def create_request():
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "client": ("127.0.0.1", 8000),
            "scheme": "http",
        }
    )


@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = RedisRateLimiter(
        limit=2,
        window=60,
        key_prefix="test",
    )

    request = create_request()

    await limiter(request)
    await limiter(request)

    with pytest.raises(HTTPException) as exc_info:
        await limiter(request)

    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Too many requests" in exc_info.value.detail