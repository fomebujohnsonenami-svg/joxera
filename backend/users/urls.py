from django.urls import path

from .auth_views import (
    GoogleSessionView,
    KycSimulateApproveView,
    KycStartView,
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    RegisterView,
)
from .views import PublicProfileView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/google/session/", GoogleSessionView.as_view(), name="auth-google-session"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/kyc/start/", KycStartView.as_view(), name="auth-kyc-start"),
    path("auth/kyc/simulate-approve/", KycSimulateApproveView.as_view(), name="auth-kyc-simulate"),
    path("profiles/<str:handle>/", PublicProfileView.as_view(), name="public-profile"),
]
