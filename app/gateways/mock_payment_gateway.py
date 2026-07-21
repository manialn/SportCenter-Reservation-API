from decimal import Decimal
from uuid import uuid4

from app.enumsfile.enum import PaymentStatus
from app.gateways.payment_gateway import PaymentGateway


class MockPaymentGateway(PaymentGateway):

    async def create_payment(
        self,
        amount: Decimal,
    ) -> tuple[str, PaymentStatus]:
        return str(uuid4()), PaymentStatus.SUCCESS