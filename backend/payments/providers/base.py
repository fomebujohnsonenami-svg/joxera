from abc import ABC, abstractmethod
from decimal import Decimal

from django.http import HttpRequest

from users.models import User

from .types import EscrowPaymentResult, PayoutResult, SettlementEvent


class PayoutProvider(ABC):
    """Swappable payout rail — Stripe Connect (cards/bank) or dLocal (Mobile Money/Pix)."""

    provider_name: str

    @abstractmethod
    def create_escrow_payment(
        self,
        *,
        employer: User,
        amount: Decimal,
        currency: str,
        escrow_id: int,
        metadata: dict | None = None,
    ) -> EscrowPaymentResult:
        """Initiate employer funding for an escrow."""

    @abstractmethod
    def initiate_payout(
        self,
        *,
        talent: User,
        amount: Decimal,
        currency: str,
        rail: str,
        metadata: dict | None = None,
    ) -> PayoutResult:
        """Send funds to talent via regional rail."""

    @abstractmethod
    def verify_webhook_signature(self, request: HttpRequest) -> bool:
        """Validate inbound webhook authenticity."""

    @abstractmethod
    def parse_webhook(self, request: HttpRequest) -> SettlementEvent:
        """Parse a verified webhook into a normalized settlement event."""
