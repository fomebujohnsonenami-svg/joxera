from django.urls import path

from .views import (
    CreateEscrowView,
    FundEscrowView,
    PaymentWebhookView,
    ReleaseEscrowView,
    SeedWalletView,
    WalletDashboardView,
)

urlpatterns = [
    path("payments/wallet/", WalletDashboardView.as_view(), name="payments-wallet"),
    path("payments/escrow/create/", CreateEscrowView.as_view(), name="payments-escrow-create"),
    path("payments/escrow/fund/", FundEscrowView.as_view(), name="payments-escrow-fund"),
    path("payments/wallet/seed/", SeedWalletView.as_view(), name="payments-wallet-seed"),
    path("payments/release-escrow/", ReleaseEscrowView.as_view(), name="payments-release-escrow"),
    path("payments/webhook/", PaymentWebhookView.as_view(), name="payments-webhook"),
]
