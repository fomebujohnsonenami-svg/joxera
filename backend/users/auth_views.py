
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from users.models import KYCStatus, User

from .serializers import RegisterSerializer, UserPublicSerializer


def _tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserPublicSerializer(user).data,
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(_tokens_for_user(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password", "")
        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(_tokens_for_user(user))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class KycStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "redirectUrl": None,
                "detail": "Use /api/auth/kyc/simulate-approve/ in development.",
            }
        )


class KycSimulateApproveView(APIView):
    """Development/E2E helper — approve KYC without external provider."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.DEBUG and not getattr(settings, "ALLOW_KYC_SIMULATION", False):
            return Response({"detail": "Not available."}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        user.kyc_status = KYCStatus.APPROVED
        user.verified_badge = True
        user.save(update_fields=["kyc_status", "verified_badge"])
        return Response(UserPublicSerializer(user).data)


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []
