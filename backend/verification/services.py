import logging

from django.db import transaction

from users.models import KYCStatus, User

from .models import VerificationSession
from .providers.registry import get_identity_provider
from .providers.types import VerificationOutcome

logger = logging.getLogger(__name__)

_OUTCOME_TO_KYC = {
    VerificationOutcome.PENDING: KYCStatus.PENDING,
    VerificationOutcome.SUBMITTED: KYCStatus.SUBMITTED,
    VerificationOutcome.APPROVED: KYCStatus.APPROVED,
    VerificationOutcome.REJECTED: KYCStatus.REJECTED,
}

_OUTCOME_TO_SESSION = {
    VerificationOutcome.PENDING: VerificationSession.SessionStatus.PENDING,
    VerificationOutcome.SUBMITTED: VerificationSession.SessionStatus.SUBMITTED,
    VerificationOutcome.APPROVED: VerificationSession.SessionStatus.APPROVED,
    VerificationOutcome.REJECTED: VerificationSession.SessionStatus.REJECTED,
}


@transaction.atomic
def start_verification(user: User) -> VerificationSession:
    provider = get_identity_provider()
    result = provider.create_session(user)

    session = VerificationSession.objects.create(
        user=user,
        provider=result.provider,
        external_session_id=result.external_session_id,
        redirect_url=result.redirect_url,
        status=VerificationSession.SessionStatus.CREATED,
    )

    User.objects.filter(pk=user.pk).update(kyc_status=KYCStatus.PENDING)
    logger.info("KYC session started for user %s via %s", user.pk, result.provider)
    return session


@transaction.atomic
def process_verification_event(event) -> User | None:
    """Apply a normalized webhook event to the matching user."""

    try:
        session = VerificationSession.objects.select_for_update().get(
            external_session_id=event.external_session_id
        )
    except VerificationSession.DoesNotExist:
        logger.warning(
            "Webhook for unknown session %s from %s",
            event.external_session_id,
            event.provider,
        )
        return None

    kyc_status = _OUTCOME_TO_KYC.get(event.outcome, KYCStatus.PENDING)
    session_status = _OUTCOME_TO_SESSION.get(
        event.outcome, VerificationSession.SessionStatus.PENDING
    )

    session.status = session_status
    session.save(update_fields=["status", "updated_at"])

    user = session.user
    user.kyc_status = kyc_status
    user.save(update_fields=["kyc_status"])

    logger.info(
        "User %s kyc_status → %s (event %s)",
        user.pk,
        kyc_status,
        event.provider_event_id,
    )
    return user
