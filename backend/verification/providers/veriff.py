import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpRequest

from users.models import User

from .base import IdentityProvider
from .types import VerificationEvent, VerificationOutcome, VerificationSessionResult

logger = logging.getLogger(__name__)


class VeriffProvider(IdentityProvider):
    provider_name = "veriff"

    def __init__(self) -> None:
        self.api_key = getattr(settings, "VERIFF_API_KEY", "")
        self.api_secret = getattr(settings, "VERIFF_API_SECRET", "")
        self.webhook_secret = getattr(settings, "VERIFF_WEBHOOK_SECRET", "")
        self.base_url = getattr(settings, "VERIFF_BASE_URL", "https://stationapi.veriff.com")

    def create_session(self, user: User) -> VerificationSessionResult:
        external_id = f"veriff_{user.pk}_{user.handle}"
        redirect_url = f"https://magic.veriff.me/v/{external_id}"
        if self.api_key:
            logger.info("Veriff session stub for user %s — wire API in production", user.pk)
        return VerificationSessionResult(
            external_session_id=external_id,
            redirect_url=redirect_url,
            provider=self.provider_name,
        )

    def verify_webhook_signature(self, request: HttpRequest) -> bool:
        secret = self.webhook_secret or self.api_secret
        if not secret:
            logger.warning("VERIFF_WEBHOOK_SECRET not configured — rejecting webhook")
            return False

        received = request.META.get("HTTP_X_HMAC_SIGNATURE", "")
        if not received:
            received = request.META.get("HTTP_X_AUTH_CLIENT", "")

        expected = hmac.new(
            secret.encode(), request.body, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(received.lower(), expected.lower())

    def parse_webhook(self, request: HttpRequest) -> VerificationEvent:
        payload = json.loads(request.body.decode("utf-8"))
        verification = payload.get("verification", payload)
        external_id = verification.get("id", verification.get("sessionId", ""))
        decision = verification.get("status", verification.get("decision", "")).lower()

        return VerificationEvent(
            external_session_id=str(external_id),
            outcome=self._map_decision(decision),
            provider=self.provider_name,
            provider_event_id=str(payload.get("id", external_id)),
            raw_payload=payload,
        )

    @staticmethod
    def _map_decision(decision: str) -> VerificationOutcome:
        mapping = {
            "created": VerificationOutcome.PENDING,
            "started": VerificationOutcome.PENDING,
            "submitted": VerificationOutcome.SUBMITTED,
            "approved": VerificationOutcome.APPROVED,
            "declined": VerificationOutcome.REJECTED,
            "expired": VerificationOutcome.REJECTED,
            "abandoned": VerificationOutcome.REJECTED,
        }
        return mapping.get(decision, VerificationOutcome.PENDING)
