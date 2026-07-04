from abc import ABC, abstractmethod

from django.http import HttpRequest

from users.models import User

from .types import VerificationEvent, VerificationSessionResult


class IdentityProvider(ABC):
    """Swappable identity-verification orchestrator (Persona, Veriff, …)."""

    provider_name: str

    @abstractmethod
    def create_session(self, user: User) -> VerificationSessionResult:
        """Start a KYC flow and return a redirect URL for the user."""

    @abstractmethod
    def verify_webhook_signature(self, request: HttpRequest) -> bool:
        """Validate the HMAC signature on an inbound provider webhook."""

    @abstractmethod
    def parse_webhook(self, request: HttpRequest) -> VerificationEvent:
        """Parse a verified webhook into a normalized VerificationEvent."""
