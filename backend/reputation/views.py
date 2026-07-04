import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.signing import VerificationError, public_key_b64, verify_reference

from .models import Reference
from .serializers import ReferenceSerializer

logger = logging.getLogger(__name__)


class VerifyReferenceView(APIView):
    """
    Public signature verification for proof-of-work credentials.

    GET /api/v3/global/references/verify/{reference_id}/
    GET /api/v3/global/references/verify/?hash={signature_hash}
    """

    permission_classes = [AllowAny]

    def get(self, request, reference_id: int | None = None):
        sig_hash = request.query_params.get("hash")

        if reference_id is not None:
            try:
                reference = Reference.objects.select_related("user", "listing").get(pk=reference_id)
            except Reference.DoesNotExist:
                return Response({"valid": False, "detail": "Reference not found."}, status=status.HTTP_404_NOT_FOUND)
        elif sig_hash:
            try:
                reference = Reference.objects.select_related("user", "listing").get(signature_hash=sig_hash)
            except Reference.DoesNotExist:
                return Response({"valid": False, "detail": "Reference not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"detail": "Provide reference_id in path or ?hash= query param."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = verify_reference(
                reference.signed_proof,
                reference.signature_b64,
                reference.signature_hash,
            )
        except VerificationError as exc:
            return Response(
                {
                    "valid": False,
                    "reference_id": reference.id,
                    "detail": str(exc),
                    "public_key": public_key_b64(),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                **result,
                "reference_id": reference.id,
                "reference": ReferenceSerializer(reference).data,
            }
        )


class PublicKeyView(APIView):
    """GET /api/v3/global/references/public-key/ — server Ed25519 public key."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"public_key": public_key_b64(), "algorithm": "Ed25519"})
