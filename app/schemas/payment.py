from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel,ConfigDict
from datetime import datetime
from app.enumsfile.enum import PaymentMethod,PaymentStatus

class PaymentCreateResponse(BaseModel):
    id: UUID
    payment_status: PaymentStatus

class PaymentResponse(BaseModel):
    id: UUID
    amount: Decimal
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    created_at: datetime
    updated_at: datetime