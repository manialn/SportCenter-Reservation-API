import uuid
from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime,Text,Enum,Numeric,Time,Index,Date,UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.enumsfile.enum import UserRole,FacilityType,BookingStatus,PaymentMethod,PaymentStatus,WeekDay

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, unique=True, index=True)
    phone_number = Column(String(50), nullable=False, unique=True, index=True)
    hashed_password = Column(String(225), nullable=False)
    is_phone_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    refresh_tokens = relationship("RefreshToken",back_populates="user",cascade="all, delete-orphan",passive_deletes=True)
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_token"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("user.id", ondelete="CASCADE"),nullable=False,index=True)
    jti = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")


class Facility(Base, TimestampMixin):
    __tablename__ = "facility"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    facility_type = Column(Enum(FacilityType), nullable=False)
    price_per_hour = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    timeslots = relationship("TimeSlot", back_populates="facility", cascade="all, delete-orphan", passive_deletes=True)
    schedules = relationship("FacilitySchedule", back_populates="facility", cascade="all, delete-orphan", passive_deletes=True)


class TimeSlot(Base, TimestampMixin):
    __tablename__ = "timeslot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facility.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_timeslot_facility_date", "facility_id", "date"),
        UniqueConstraint(
            "facility_id",
            "date",
            "start_time",
            "end_time",
            name="uq_timeslot_facility_date_time"
        ),
    )

    facility = relationship("Facility", back_populates="timeslots")
    bookings = relationship("Booking", back_populates="timeslot", cascade="all, delete-orphan", passive_deletes=True)


class FacilitySchedule(Base, TimestampMixin):
    __tablename__ = "facility_schedule"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facility.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Enum(WeekDay), nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    slot_duration = Column(Integer, nullable=False)
    price_override = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
    UniqueConstraint(
        "facility_id",
        "day_of_week",
        name="uq_facility_schedule_day"
    ),
)

    facility = relationship("Facility", back_populates="schedules")


class Booking(Base, TimestampMixin):
    __tablename__ = "booking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    timeslot_id = Column(UUID(as_uuid=True), ForeignKey("timeslot.id", ondelete="CASCADE"), nullable=False, unique=True)
    booking_status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_price = Column(Numeric(10,2), nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False,)

    user = relationship("User", back_populates="bookings")
    timeslot = relationship("TimeSlot", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan", passive_deletes=True)

class Payment(Base, TimestampMixin):
    __tablename__ = "payment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("booking.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.MOCK_GATEWAY, nullable=False)
    transaction_id = Column(String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    booking = relationship("Booking", back_populates="payment")

