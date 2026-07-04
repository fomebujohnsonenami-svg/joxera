import logging

from django.conf import settings
from django.db.models import Sum
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Listing
from users.models import User

from .models import Escrow, EscrowState, WalletTransaction
from .providers.registry import get_provider_by_name, get_provider_for_rail
from .serializers import (
    CreateEscrowSerializer,
    EscrowSerializer,
    EscrowTimelineSerializer,
    FundEscrowSerializer,
    ReleaseEscrowSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
)
from .services.escrow import (
    EscrowError,
    InsufficientFundsError,
    InvalidEscrowStateError,
    create_escrow_for_listing,
    get_or_create_wallet,
    lock_escrow_from_wallet,
    release_escrow,
    sign_off_escrow,
)
from .services.webhooks import handle_settlement_event

logger = logging.getLogger(__name__)


def _escrow_timeline(escrow: Escrow) -> list[dict]:
    """Build interactive lifecycle steps for the UI."""
    state = escrow.state

    def step_status(step_key: str) -> str:
        order = ["fund", "locked", "signoff", "released"]
        current_idx = {
            EscrowState.PENDING: 0,
            EscrowState.LOCKED: 1 if not escrow.both_signed_off else 2,
            EscrowState.RELEASED: 3,
            EscrowState.REFUNDED: 3,
        }.get(state, 0)
        step_idx = order.index(step_key)
        if step_idx < current_idx:
            return "complete"
        if step_idx == current_idx:
            return "active"
        return "pending"

    return [
        {
            "key": "fund",
            "title": "Employer funds escrow",
            "description": "Payment captured via Stripe or dLocal",
            "status": step_status("fund"),
            "at": escrow.funded_at.isoformat() if escrow.funded_at else None,
        },
        {
            "key": "locked",
            "title": "Funds locked",
            "description": "Escrow holds payment until work is verified",
            "status": step_status("locked"),
            "at": escrow.funded_at.isoformat() if escrow.funded_at else None,
        },
        {
            "key": "signoff",
            "title": "Both parties sign off",
            "description": f"Employer: {'✓' if escrow.employer_signed_off else '…'} · Talent: {'✓' if escrow.talent_signed_off else '…'}",
            "status": step_status("signoff"),
            "at": None,
        },
        {
            "key": "released",
            "title": "Released to talent wallet",
            "description": "Funds credited to talent balance",
            "status": step_status("released"),
            "at": escrow.released_at.isoformat() if escrow.released_at else None,
        },
    ]


class WalletDashboardView(APIView):
    """GET /api/v3/global/payments/wallet/ — balance, transactions, escrows."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_or_create_wallet(request.user)
        transactions = WalletTransaction.objects.filter(wallet=wallet).select_related(
            "escrow", "escrow__listing"
        )[:50]

        escrows_qs = Escrow.objects.filter(
            models_q_for_user(request.user)
        ).select_related("listing", "employer", "talent").order_by("-updated_at")[:20]

        locked_total = (
            Escrow.objects.filter(employer=request.user, state=EscrowState.LOCKED)
            .aggregate(total=Sum("amount"))["total"]
        ) or 0

        timelines = []
        for escrow in escrows_qs:
            timelines.append(
                {
                    "escrow_id": escrow.id,
                    "listing_title": escrow.listing.title,
                    "amount": escrow.amount,
                    "currency": escrow.currency,
                    "state": escrow.state,
                    "employer_signed_off": escrow.employer_signed_off,
                    "talent_signed_off": escrow.talent_signed_off,
                    "funded_at": escrow.funded_at,
                    "released_at": escrow.released_at,
                    "steps": _escrow_timeline(escrow),
                }
            )

        return Response(
            {
                "wallet": WalletSerializer(wallet).data,
                "transactions": WalletTransactionSerializer(transactions, many=True).data,
                "escrows": EscrowSerializer(escrows_qs, many=True).data,
                "escrow_timelines": EscrowTimelineSerializer(timelines, many=True).data,
                "locked_escrow_total": str(locked_total),
            }
        )


def models_q_for_user(user: User):
    from django.db.models import Q

    return Q(employer=user) | Q(talent=user)


class CreateEscrowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateEscrowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            listing = Listing.objects.get(pk=data["listing_id"], owner=request.user)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found."}, status=status.HTTP_404_NOT_FOUND)

        talent = None
        if data.get("talent_id"):
            try:
                talent = User.objects.get(pk=data["talent_id"])
            except User.DoesNotExist:
                return Response({"detail": "Talent not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            escrow = create_escrow_for_listing(listing, request.user, talent=talent)
        except EscrowError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        provider = get_provider_for_rail(get_or_create_wallet(request.user).rail)
        payment = provider.create_escrow_payment(
            employer=request.user,
            amount=escrow.amount,
            currency=escrow.currency,
            escrow_id=escrow.id,
        )
        escrow.provider_ref = payment.provider_ref
        escrow.save(update_fields=["provider_ref", "updated_at"])

        return Response(
            {
                "escrow": EscrowSerializer(escrow).data,
                "checkout_url": payment.checkout_url,
                "provider_ref": payment.provider_ref,
            },
            status=status.HTTP_201_CREATED,
        )


class FundEscrowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FundEscrowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        escrow_id = serializer.validated_data["escrow_id"]

        if serializer.validated_data.get("use_wallet"):
            try:
                escrow = lock_escrow_from_wallet(escrow_id, request.user)
            except InsufficientFundsError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            except (EscrowError, InvalidEscrowStateError) as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"escrow": EscrowSerializer(escrow).data})

        return Response(
            {"detail": "External funding is confirmed via payment webhook."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReleaseEscrowView(APIView):
    """
    POST /api/v3/global/payments/release-escrow/

    Records sign-off from the authenticated party; when both employer and talent
    have signed off, atomically releases escrow to the talent wallet.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReleaseEscrowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        escrow_id = serializer.validated_data["escrow_id"]

        try:
            escrow = sign_off_escrow(escrow_id, request.user)
        except (EscrowError, InvalidEscrowStateError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        released = False
        if escrow.both_signed_off and escrow.state == EscrowState.LOCKED:
            try:
                escrow = release_escrow(escrow_id)
                released = True

                if escrow.talent_id:
                    provider = get_provider_by_name(escrow.provider)
                    talent_wallet = get_or_create_wallet(escrow.talent)
                    provider.initiate_payout(
                        talent=escrow.talent,
                        amount=escrow.amount,
                        currency=escrow.currency,
                        rail=talent_wallet.rail,
                        metadata={"escrow_id": str(escrow.id)},
                    )
            except (EscrowError, InvalidEscrowStateError) as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "escrow": EscrowSerializer(escrow).data,
                "released": released,
                "timeline": _escrow_timeline(escrow),
            }
        )


class PaymentWebhookView(APIView):
    """
    Ingest Stripe / dLocal settlement webhooks.

    POST /api/v3/global/payments/webhook/?provider=stripe|dlocal
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        provider_name = request.query_params.get("provider", "stripe").lower()
        try:
            provider = get_provider_by_name(provider_name)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not provider.verify_webhook_signature(request):
            logger.warning("Rejected payment webhook with invalid signature (%s)", provider_name)
            return Response(
                {"detail": "Invalid webhook signature."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            event = provider.parse_webhook(request)
        except Exception as exc:
            logger.exception("Failed to parse payment webhook")
            return Response(
                {"detail": f"Malformed webhook payload: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = handle_settlement_event(event)
        return Response(result)


class SeedWalletView(APIView):
    """Development/E2E helper — credit the authenticated user's wallet."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.DEBUG and not getattr(settings, "ALLOW_KYC_SIMULATION", False):
            return Response({"detail": "Not available."}, status=status.HTTP_403_FORBIDDEN)
        from decimal import Decimal

        amount = Decimal(str(request.data.get("amount", "10000")))
        wallet = get_or_create_wallet(request.user)
        wallet.balance += amount
        wallet.save(update_fields=["balance", "updated_at"])
        return Response(WalletSerializer(wallet).data)
