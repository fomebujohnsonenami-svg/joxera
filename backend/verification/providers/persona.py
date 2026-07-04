import hashlib
import hmac
import json
import logging
import re

from django.conf import settings
from django.http import HttpRequest

from users.models import User

from .base import IdentityProvider
from .types import VerificationEvent, VerificationOutcome, VerificationSessionResult

logger = logging.getLogger(__name__)

_PERSONA_SIG_RE = re.compile(r"t=(?P<t>[^,]+),v1=(?P<v1>[a-f0-9]+)")


class PersonaProvider(IdentityProvider):
    provider_name = "persona"

    def __init__(self) -> None:
        self.api_key = getattr(settings, "PERSONA_API_KEY", "")
        self.template_id = getattr(settings, "PERSONA_TEMPLATE_ID", "")
        self.webhook_secret = getattr(settings, "PERSONA_WEBHOOK_SECRET", "")
        self.base_url = getattr(
            settings, "PERSONA_BASE_URL", "https://withpersona.com/api/v1"
        )

    def create_session(self, user: User) -> VerificationSessionResult:
        external_id = f"inq_{user.pk}_{user.handle}"
        redirect_url = (
            f"https://withpersona.com/verify?"
            f"inquiry-id={external_id}&reference-id={user.pk}"
        )
        if self.api_key and self.template_id:
            logger.info("Persona session stub for user %s — wire API in production", user.pk)
        return VerificationSessionResult(
            external_session_id=external_id,
            redirect_url=redirect_url,
            provider=self.provider_name,
        )

    def verify_webhook_signature(self, request: HttpRequest) -> bool:
        secret = self.webhook_secret
        if not secret:
            logger.warning("PERSONA_WEBHOOK_SECRET not configured — rejecting webhook")
            return False

        signature_header = request.META.get("HTTP_PERSONA_SIGNATURE", "")
        match = _PERSONA_SIG_RE.search(signature_header)
        if not match:
            return False

        timestamp = match.group("t")
        received_sig = match.group("v1")
        body = request.body

        signed_payload = f"{timestamp}.".encode() + body
        expected = hmac.new(
            secret.encode(), signed_payload, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(received_sig, expected)

    def parse_webhook(self, request: HttpRequest) -> VerificationEvent:
        payload = json.loads(request.body.decode("utf-8"))
        data = payload.get("data", {})
        attributes = data.get("attributes", {})
        external_id = data.get("id", "")

        status_raw = attributes.get("status", "").lower()
        outcome = self._map_status(status_raw)

        return VerificationEvent(
            external_session_id=external_id,
            outcome=outcome,
            provider=self.provider_name,
            provider_event_id=payload.get("id", external_id),
            raw_payload=payload,
        )

    @staticmethod
    def _map_status(status: str) -> VerificationOutcome:
        mapping = {
            "created": VerificationOutcome.PENDING,
            "pending": VerificationOutcome.PENDING,
            "completed": VerificationOutcome.SUBMITTED,
            "approved": VerificationOutcome.APPROVED,
            "declined": VerificationOutcome.REJECTED,
            "failed": VerificationOutcome.REJECTED,
        }
        return mapping.get(status, VerificationOutcome.PENDING)
