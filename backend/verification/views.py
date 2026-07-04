import logging

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from verification.providers.registry import get_identity_provider

from .services import process_verification_event

logger = logging.getLogger(__name__)


class VerificationWebhookViewSet(viewsets.ViewSet):
    """
    Ingest identity-provider webhook events.

    POST /api/v3/global/verification/webhook/
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request):
        provider = get_identity_provider()

        if not provider.verify_webhook_signature(request):
            logger.warning(
                "Rejected webhook with invalid HMAC from %s",
                provider.provider_name,
            )
            return Response(
                {"detail": "Invalid webhook signature."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            event = provider.parse_webhook(request)
        except (ValueError, KeyError) as exc:
            logger.exception("Failed to parse webhook payload")
            return Response(
                {"detail": f"Malformed webhook payload: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = process_verification_event(event)
        if user is None:
            return Response(
                {"detail": "Unknown verification session."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "status": "processed",
                "user_id": user.pk,
                "kyc_status": user.kyc_status,
                "verified_badge": user.verified_badge,
            },
            status=status.HTTP_200_OK,
        )


# Alias for explicit URL wiring
VerificationWebhookView = VerificationWebhookViewSet
