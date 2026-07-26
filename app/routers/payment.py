from fastapi import APIRouter,status,Depends
from uuid import UUID
from app.core.dependency import db_dependency,user_dependency
from app.schemas.payment import (
    PaymentResponse,PaymentCreateResponse                
)
from app.services.payment_service import (
    create_payment_service,get_payment_service
)
from app.limiter.rate_limiter import RedisRateLimiter

router = APIRouter(
    prefix="/payments"
)

@router.post("/{booking_id}",status_code=status.HTTP_201_CREATED,response_model=PaymentCreateResponse)
async def create_payment(booking_id: UUID,user: user_dependency,
    db: db_dependency, _: None = Depends(
        RedisRateLimiter(
            limit=5,
            window=60,
            key_prefix="payment",
        )
    ),):
    return await create_payment_service(booking_id=booking_id,user_id=user.id,db=db)

#@router.post("/callback",status_code=status.HTTP_200_OK)

@router.get("/{payment_id}",status_code=status.HTTP_200_OK,response_model=PaymentResponse)
async def get_payment(payment_id: UUID,user: user_dependency,
    db: db_dependency):
    return await get_payment_service(payment_id=payment_id,user_id=user.id,db=db)
