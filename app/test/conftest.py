import os

os.environ["ENV_FILE"] = ".env.test"

from contextlib import AsyncExitStack
from datetime import timedelta
import uuid

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.redis_client import get_redis
from app.core.security import hash_password
from app.core.token import create_access_token, create_refresh_token
from app.database import Base, get_db
from app.enumsfile.enum import UserRole
from app.main import app
from app.models import User


@pytest_asyncio.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    return engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session(test_engine):
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture
async def override_db(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override

    yield

    app.dependency_overrides.clear()


# ---------- lifespan فقط یک بار ----------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def app_lifespan():
    async with app.router.lifespan_context(app):
        yield


# ---------- client ----------
@pytest_asyncio.fixture
async def client(app_lifespan, override_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# ---------- redis ----------
@pytest_asyncio.fixture(autouse=True)
async def clear_redis():
    yield


@pytest_asyncio.fixture
async def user_factory(db_session):
    async def create_user(
        username=None,
        phone_number=None,
        password="12345678",
        role=None,
        is_active=True,
        is_phone_verified=True,
    ):
        user = User(
            username=username or f"user_{uuid.uuid4().hex[:8]}",
            phone_number=phone_number or f"09{uuid.uuid4().int % 1000000000:09d}",
            hashed_password=hash_password(password),
            role=role or UserRole.USER,
            is_active=is_active,
            is_phone_verified=is_phone_verified,
        )

        db_session.add(user)

        await db_session.commit()
        await db_session.refresh(user)

        return user

    return create_user


@pytest_asyncio.fixture
async def admin_user(user_factory):
    return await user_factory(role=UserRole.ADMIN)


@pytest_asyncio.fixture
async def test_user(user_factory):
    return await user_factory()


@pytest_asyncio.fixture
async def access_token(test_user):
    return create_access_token(
        test_user.id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@pytest_asyncio.fixture
async def refresh_token(test_user):
    return create_refresh_token(
        test_user.id,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


@pytest_asyncio.fixture
async def admin_access_token(admin_user):
    return create_access_token(
        admin_user.id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@pytest_asyncio.fixture
async def authorized_client(client, access_token):
    client.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
        }
    )
    return client
    






