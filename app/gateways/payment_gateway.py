from abc import ABC, abstractmethod
from decimal import Decimal

from app.enumsfile.enum import PaymentStatus


class PaymentGateway(ABC):

    @abstractmethod
    async def create_payment(
        self,
        amount: Decimal,
    ) -> tuple[str, PaymentStatus]:
        pass