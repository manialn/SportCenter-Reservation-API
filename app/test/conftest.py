import os

os.environ["ENV_FILE"] = ".env.test"

from datetime import timedelta,time
from datetime import date as dt_date, time as dt_time
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
from app.enumsfile.enum import UserRole,FacilityType,WeekDay,BookingStatus,PaymentMethod,PaymentStatus
from app.main import app
from app.models import User,Facility,FacilitySchedule,TimeSlot,Booking,Payment


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

@pytest_asyncio.fixture
async def authorized_admin_client(client, admin_access_token):
    client.headers.update(
        {
            "Authorization": f"Bearer {admin_access_token}",
        }
    )
    return client

@pytest_asyncio.fixture
async def facility_factory(db_session):
    async def create_facility(
        name=None,
        description=None,
        facility_type=FacilityType.FOOTBALL,
        price_per_hour=100,
        is_active=True,
    ):
        facility = Facility(
            name=name or f"facility_{uuid.uuid4().hex[:8]}",
            description=description,
            facility_type=facility_type,
            price_per_hour=price_per_hour,
            is_active=is_active,
        )

        db_session.add(facility)

        await db_session.commit()
        await db_session.refresh(facility)

        return facility

    return create_facility

@pytest_asyncio.fixture
async def facility_schedule_factory(db_session):
    async def create_schedule(
        facility_id,
        day_of_week=WeekDay.MONDAY,
        open_time=time(8, 0),
        close_time=time(22, 0),
        slot_duration=60,
        price_override=None,
        is_active=True,
    ):
        schedule = FacilitySchedule(
            facility_id=facility_id,
            day_of_week=day_of_week,
            open_time=open_time,
            close_time=close_time,
            slot_duration=slot_duration,
            price_override=price_override,
            is_active=is_active,
        )

        db_session.add(schedule)

        await db_session.commit()
        await db_session.refresh(schedule)

        return schedule

    return create_schedule

@pytest_asyncio.fixture
async def timeslot_factory(db_session):
    
    async def create_timeslot(
        facility_id,
        date=None,
        start_time=None,
        end_time=None,
        is_active=True,
    ):
        final_date = date or dt_date(2026, 7, 13)
        final_start = start_time or dt_time(9, 0)
        final_end = end_time or dt_time(10, 0)

        timeslot = TimeSlot(
            facility_id=facility_id,
            date=final_date,
            start_time=final_start,
            end_time=final_end,
            is_active=is_active,
        )

        db_session.add(timeslot)
        await db_session.commit()
        await db_session.refresh(timeslot)

        return timeslot

    return create_timeslot

@pytest_asyncio.fixture
async def booking_factory(db_session):
    async def create_booking(
        user_id,
        timeslot_id,
        booking_status=BookingStatus.PENDING,
        total_price=100,
    ):
        booking = Booking(
            user_id=user_id,
            timeslot_id=timeslot_id,
            booking_status=booking_status,
            total_price=total_price,
        )

        db_session.add(booking)

        await db_session.commit()
        await db_session.refresh(booking)

        return booking

    return create_booking

@pytest_asyncio.fixture
async def payment_factory(db_session):
    async def create_payment(
        booking_id,
        amount=100,
        payment_status=PaymentStatus.SUCCESS,
        payment_method=PaymentMethod.MOCK_GATEWAY,
        transaction_id=None,
    ):
        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_status=payment_status,
            payment_method=payment_method,
            transaction_id=transaction_id or str(uuid.uuid4()),
        )

        db_session.add(payment)

        await db_session.commit()
        await db_session.refresh(payment)

        return payment

    return create_payment

    






