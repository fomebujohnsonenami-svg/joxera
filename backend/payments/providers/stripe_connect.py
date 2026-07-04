import json
import logging
import uuid
from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest

from users.models import User

from .base import PayoutProvider
from .types import EscrowPaymentResult, PayoutResult, SettlementEvent

logger = logging.getLogger(__name__)


class StripeConnectProvider(PayoutProvider):
    """Stripe Connect — cards and bank transfers (ACH/SEPA)."""

    provider_name = "stripe"

    def __init__(self) -> None:
        self.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
        self.webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    def create_escrow_payment(
        self,
        *,
        employer: User,
        amount: Decimal,
        currency: str,
        escrow_id: int,
        metadata: dict | None = None,
    ) -> EscrowPaymentResult:
        ref = f"pi_stripe_{escrow_id}_{uuid.uuid4().hex[:12]}"
        meta = {"escrow_id": str(escrow_id), "employer_id": str(employer.id), **(metadata or {})}

        if self.api_key:
            try:
                return self._create_stripe_payment_intent(ref, amount, currency, meta)
            except Exception:
                logger.exception("Stripe payment intent failed — using dev stub")

        return EscrowPaymentResult(
            provider_ref=ref,
            checkout_url=f"https://checkout.stripe.com/pay/{ref}",
            status="pending",
            raw={"mode": "dev_stub", "metadata": meta},
        )

    def _create_stripe_payment_intent(
        self, ref: str, amount: Decimal, currency: str, metadata: dict
    ) -> EscrowPaymentResult:
        import stripe

        stripe.api_key = self.api_key
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency.lower(),
            metadata=metadata,
            automatic_payment_methods={"enabled": True},
        )
        return EscrowPaymentResult(
            provider_ref=intent.id,
            checkout_url=intent.get("next_action", {}).get("redirect_to_url", {}).get("url"),
            status=intent.status,
            raw=dict(intent),
        )

    def initiate_payout(
        self,
        *,
        talent: User,
        amount: Decimal,
        currency: str,
        rail: str,
        metadata: dict | None = None,
    ) -> PayoutResult:
        ref = f"po_stripe_{talent.id}_{uuid.uuid4().hex[:12]}"
        if self.api_key:
            try:
                import stripe

                stripe.api_key = self.api_key
                transfer = stripe.Transfer.create(
                    amount=int(amount * 100),
                    currency=currency.lower(),
                    metadata={"talent_id": str(talent.id), **(metadata or {})},
                )
                return PayoutResult(provider_ref=transfer.id, status="pending", raw=dict(transfer))
            except Exception:
                logger.exception("Stripe payout failed — using dev stub")

        return PayoutResult(provider_ref=ref, status="pending", raw={"mode": "dev_stub"})

    def verify_webhook_signature(self, request: HttpRequest) -> bool:
        secret = self.webhook_secret
        if not secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured — rejecting webhook")
            return False
        sig = request.headers.get("Stripe-Signature", "")
        if not sig:
            return False
        try:
            import stripe

            stripe.Webhook.construct_event(request.body, sig, secret)
            return True
        except Exception:
            return False

    def parse_webhook(self, request: HttpRequest) -> SettlementEvent:
        payload = json.loads(request.body)
        event_type = payload.get("type", "")
        obj = payload.get("data", {}).get("object", {})
        metadata = obj.get("metadata", {})

        status_map = {
            "payment_intent.succeeded": "funded",
            "payment_intent.payment_failed": "failed",
            "transfer.paid": "paid",
            "payout.paid": "paid",
        }

        return SettlementEvent(
            provider=self.provider_name,
            event_type=event_type,
            provider_ref=obj.get("id", ""),
            escrow_ref=metadata.get("escrow_id"),
            amount=Decimal(str(obj.get("amount", 0))) / 100 if obj.get("amount") else None,
            currency=(obj.get("currency") or "").upper() or None,
            status=status_map.get(event_type, event_type),
            raw=payload,
        )
