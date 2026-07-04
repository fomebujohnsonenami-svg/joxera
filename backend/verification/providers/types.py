from dataclasses import dataclass
from enum import Enum
from typing import Any


class VerificationOutcome(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class VerificationSessionResult:
    """Returned when initiating a KYC session with an external provider."""

    external_session_id: str
    redirect_url: str
    provider: str


@dataclass(frozen=True)
class VerificationEvent:
    """Normalized webhook event from any identity provider."""

    external_session_id: str
    outcome: VerificationOutcome
    provider: str
    provider_event_id: str
    raw_payload: dict[str, Any]
