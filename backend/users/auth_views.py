import re
from datetime import timedelta

import httpx
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from users.models import EmergentSession, KYCStatus, User, UserRole

from .serializers import RegisterSerializer, UserPublicSerializer


def _tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserPublicSerializer(user).data,
    }


def _unique_handle(email: str) -> str:
    base = re.sub(r"[^a-z0-9_]", "", email.split("@")[0].lower())[:30] or "user"
    if len(base) < 3:
        base = f"{base}user"[:30]
    handle = base
    suffix = 1
    while User.objects.filter(handle__iexact=handle).exists():
        tail = str(suffix)
        handle = f"{base[: 30 - len(tail)]}{tail}"
        suffix += 1
    return handle


class GoogleSessionView(APIView):
    """Exchange an Emergent OAuth session_id for app JWT tokens.

    The session_id (from the URL fragment after Google login) is verified
    server-side against the Emergent Auth service; a user is created or
    matched by email, and standard JWT tokens are returned so the rest of
    the app continues to use its existing auth flow.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        session_id = request.headers.get("X-Session-ID") or request.data.get("session_id")
        if not session_id:
            return Response(
                {"detail": "Missing session id."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            resp = httpx.get(
                settings.EMERGENT_AUTH_SESSION_URL,
                headers={"X-Session-ID": session_id},
                timeout=10.0,
            )
        except httpx.HTTPError:
            return Response(
                {"detail": "Auth service unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        if resp.status_code != 200:
            return Response(
                {"detail": "Invalid or expired session."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        data = resp.json()
        email = (data.get("email") or "").strip().lower()
        if not email:
            return Response(
                {"detail": "No email returned by provider."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            handle = _unique_handle(email)
            user = User(
                username=handle,
                email=email,
                handle=handle,
                role=UserRole.TALENT,
                country_code=getattr(settings, "DEFAULT_COUNTRY", "US"),
            )
            name = (data.get("name") or "").strip()
            if name:
                parts = name.split()
                user.first_name = parts[0][:150]
                if len(parts) > 1:
                    user.last_name = " ".join(parts[1:])[:150]
            user.set_unusable_password()
            user.save()

        session_token = data.get("session_token") or ""
        if session_token:
            EmergentSession.objects.create(
                user=user,
                session_token=session_token,
                expires_at=timezone.now() + timedelta(days=7),
            )

        payload = _tokens_for_user(user)
        response = Response(payload)
        if session_token:
            response.set_cookie(
                "session_token",
                session_token,
                max_age=7 * 24 * 3600,
                httponly=True,
                secure=True,
                samesite="none",
                path="/",
            )
        return response


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
