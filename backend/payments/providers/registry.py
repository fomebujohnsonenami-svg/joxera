from core.models import PaymentRail

from .base import PayoutProvider
from .dlocal import DLocalProvider
from .stripe_connect import StripeConnectProvider

_PROVIDERS: dict[str, type[PayoutProvider]] = {
    "stripe": StripeConnectProvider,
    "dlocal": DLocalProvider,
}

_RAIL_DEFAULTS: dict[str, str] = {
    PaymentRail.CARD: "stripe",
    PaymentRail.ACH: "stripe",
    PaymentRail.SEPA: "stripe",
    PaymentRail.SWIFT: "stripe",
    PaymentRail.PIX: "dlocal",
    PaymentRail.MOBILE_MONEY: "dlocal",
    PaymentRail.UPI: "dlocal",
}


def get_payout_provider(name: str | None = None) -> PayoutProvider:
    if name:
        provider_cls = _PROVIDERS.get(name.lower())
        if provider_cls is None:
            raise ValueError(f"Unknown payment provider '{name}'. Choose from: {', '.join(_PROVIDERS)}")
        return provider_cls()
    return StripeConnectProvider()


def get_provider_for_rail(rail: str) -> PayoutProvider:
    provider_name = _RAIL_DEFAULTS.get(rail, "stripe")
    return get_payout_provider(provider_name)


def get_provider_by_name(provider: str) -> PayoutProvider:
    return get_payout_provider(provider)
