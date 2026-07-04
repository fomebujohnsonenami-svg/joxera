import hashlib
import hmac
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


class DLocalProvider(PayoutProvider):
    """dLocal — Mobile Money and Pix payouts."""

    provider_name = "dlocal"

    def __init__(self) -> None:
        self.api_key = getattr(settings, "DLOCAL_API_KEY", "")
        self.api_secret = getattr(settings, "DLOCAL_API_SECRET", "")
        self.webhook_secret = getattr(settings, "DLOCAL_WEBHOOK_SECRET", "")

    def create_escrow_payment(
        self,
        *,
        employer: User,
        amount: Decimal,
        currency: str,
        escrow_id: int,
        metadata: dict | None = None,
    ) -> EscrowPaymentResult:
        ref = f"pay_dlocal_{escrow_id}_{uuid.uuid4().hex[:12]}"
        meta = {"escrow_id": str(escrow_id), **(metadata or {})}

        if self.api_key:
            try:
                return self._create_dlocal_payment(ref, amount, currency, employer, meta)
            except Exception:
                logger.exception("dLocal payment failed — using dev stub")

        return EscrowPaymentResult(
            provider_ref=ref,
            checkout_url=f"https://pay.dlocal.com/checkout/{ref}",
            status="PENDING",
            raw={"mode": "dev_stub", "metadata": meta},
        )

    def _create_dlocal_payment(
        self, ref: str, amount: Decimal, currency: str, employer: User, metadata: dict
    ) -> EscrowPaymentResult:
        import httpx

        payload = {
            "amount": float(amount),
            "currency": currency,
            "country": employer.country_code,
            "payment_method_id": "PIX" if currency == "BRL" else "MW",
            "order_id": ref,
            "notification_url": getattr(settings, "DLOCAL_WEBHOOK_URL", ""),
            "metadata": metadata,
        }
        headers = self._auth_headers(payload)
        resp = httpx.post(
            "https://api.dlocal.com/payments",
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return EscrowPaymentResult(
            provider_ref=data.get("id", ref),
            checkout_url=data.get("redirect_url"),
            status=data.get("status", "PENDING"),
            raw=data,
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
        ref = f"payout_dlocal_{talent.id}_{uuid.uuid4().hex[:12]}"
        if self.api_key:
            try:
                import httpx

                payload = {
                    "amount": float(amount),
                    "currency": currency,
                    "country": talent.country_code,
                    "beneficiary_name": talent.handle,
                    "payout_method": "PIX" if rail == "Pix" else "MOBILE_MONEY",
                    "external_id": ref,
                }
                headers = self._auth_headers(payload)
                resp = httpx.post(
                    "https://api.dlocal.com/payouts",
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return PayoutResult(
                    provider_ref=data.get("id", ref),
                    status=data.get("status", "PENDING"),
                    raw=data,
                )
            except Exception:
                logger.exception("dLocal payout failed — using dev stub")

        return PayoutResult(provider_ref=ref, status="PENDING", raw={"mode": "dev_stub"})

    def _auth_headers(self, payload: dict) -> dict:
        body = json.dumps(payload, separators=(",", ":"))
        signature = hmac.new(
            self.api_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()
        return {
            "X-Login": self.api_key,
            "X-Trans-Key": self.api_secret,
            "X-Version": "2.1",
            "Authorization": f"V2-HMAC-SHA256, Signature: {signature}",
            "Content-Type": "application/json",
        }

    def verify_webhook_signature(self, request: HttpRequest) -> bool:
        secret = self.webhook_secret
        if not secret:
            logger.warning("DLOCAL_WEBHOOK_SECRET not configured — rejecting webhook")
            return False
        sig = request.headers.get("X-Signature", "") or request.headers.get("Authorization", "")
        expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig.replace("Signature: ", ""), expected)

    def parse_webhook(self, request: HttpRequest) -> SettlementEvent:
        payload = json.loads(request.body)
        status = payload.get("status", "")
        metadata = payload.get("metadata", {})

        event_type = "payment.completed" if status in ("PAID", "COMPLETED") else f"payment.{status.lower()}"

        return SettlementEvent(
            provider=self.provider_name,
            event_type=event_type,
            provider_ref=payload.get("id", ""),
            escrow_ref=metadata.get("escrow_id"),
            amount=Decimal(str(payload.get("amount", 0))) if payload.get("amount") else None,
            currency=(payload.get("currency") or "").upper() or None,
            status=status.lower(),
            raw=payload,
        )
