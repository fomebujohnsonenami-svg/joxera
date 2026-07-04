from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from reputation.models import Reference
from reputation.serializers import ProofOfWorkCredentialSerializer
from users.models import KYCStatus, User


class PublicProfileView(APIView):
    """GET /api/profiles/{handle}/ — public profile with signed credentials."""

    permission_classes = [AllowAny]

    def get(self, request, handle: str):
        handle = handle.lstrip("@")
        try:
            user = User.objects.prefetch_related(
                Prefetch(
                    "references",
                    queryset=Reference.objects.select_related("listing", "listing__owner").order_by("-issued_at"),
                )
            ).get(handle__iexact=handle)
        except User.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=404)

        credentials = []
        for ref in user.references.all():
            listing = ref.listing
            credentials.append(
                {
                    "id": ref.id,
                    "job_title": listing.title,
                    "field": ref.signed_proof.get("field", listing.field),
                    "tier": ref.signed_proof.get("tier", listing.tier),
                    "completed_at": ref.signed_proof.get("timestamp", ref.issued_at.isoformat()),
                    "signed_by": listing.owner.handle,
                    "signature_hash": ref.signature_hash,
                    "verify_url": f"/api/v3/global/references/verify/{ref.id}/",
                }
            )

        return Response(
            {
                "handle": user.handle,
                "display_name": user.get_full_name() or user.handle,
                "country": user.country_code,
                "is_verified": user.kyc_status == KYCStatus.APPROVED,
                "bio": "",
                "credentials": ProofOfWorkCredentialSerializer(credentials, many=True).data,
                "references": [],
            }
        )
