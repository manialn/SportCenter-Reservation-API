from fastapi import APIRouter,status,Query,Depends
from uuid import UUID
from app.core.dependency import db_dependency,admin_dependency,user_dependency
from app.schemas.booking import (
    BookingResponse,BookingCreateRequest,BookingListResponse,BookingDetailResponse,BookingAdminResponse
    )
from app.services.booking_service import (
    create_booking_service,get_bookings_service,get_booking_detail_service,
    cancel_booking_service,get_bookings_admin_service
)
from app.limiter.rate_limiter import RedisRateLimiter


router = APIRouter(
    prefix="/bookings"
)

@router.post("",status_code=status.HTTP_201_CREATED,response_model=BookingResponse)
async def create_booking(request: BookingCreateRequest,user: user_dependency,
    db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=10,
            window=60,
            key_prefix="booking",
        )
    ),):
    return await create_booking_service(user_id=user.id,
        timeslot_id=request.timeslot_id,db=db,)

@router.get("",status_code=status.HTTP_200_OK,response_model=list[BookingListResponse])
async def get_bookings(user: user_dependency,db: db_dependency,
    page: int = Query(1, ge=1),page_size: int = Query(10, ge=1, le=100)):
    return await get_bookings_service(user_id=user.id,page=page,
        page_size=page_size,db=db)

@router.patch("/{booking_id}/cancel",status_code=status.HTTP_200_OK)
async def cancel_booking(booking_id: UUID,user: user_dependency,
    db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=10,
            window=60,
            key_prefix="cancel_booking",
        )
    ),):
    return await cancel_booking_service(booking_id=booking_id,user_id=user.id,db=db)

@router.get("/admin",status_code=status.HTTP_200_OK,response_model=list[BookingAdminResponse])
async def get_bookings_admin(admin: admin_dependency,db: db_dependency,
    page: int = Query(1, ge=1),page_size: int = Query(10, ge=1, le=100)):
    return await get_bookings_admin_service(page=page,page_size=page_size,db=db)

@router.get("/{booking_id}",status_code=status.HTTP_200_OK,response_model=BookingDetailResponse)
async def get_booking_detail(booking_id: UUID,user: user_dependency,
    db: db_dependency):
    return await get_booking_detail_service(booking_id=booking_id,user_id=user.id,db=db)
    