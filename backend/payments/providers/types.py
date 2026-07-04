from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class EscrowPaymentResult:
    provider_ref: str
    checkout_url: str | None = None
    status: str = "pending"
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class PayoutResult:
    provider_ref: str
    status: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SettlementEvent:
    """Normalized settlement webhook from Stripe or dLocal."""

    provider: str
    event_type: str
    provider_ref: str
    escrow_ref: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    status: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
