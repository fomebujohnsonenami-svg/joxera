from django.contrib import admin

from .models import Escrow, Wallet, WalletTransaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "currency", "balance", "rail", "updated_at")
    list_filter = ("currency", "rail")
    search_fields = ("user__handle", "user__email")
    raw_id_fields = ("user",)


@admin.register(Escrow)
class EscrowAdmin(admin.ModelAdmin):
    list_display = (
        "listing",
        "employer",
        "talent",
        "amount",
        "currency",
        "state",
        "provider",
        "employer_signed_off",
        "talent_signed_off",
    )
    list_filter = ("state", "currency", "provider")
    search_fields = ("listing__title", "employer__handle", "talent__handle", "provider_ref")
    raw_id_fields = ("listing", "employer", "talent")


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "tx_type", "amount", "currency", "balance_after", "created_at")
    list_filter = ("tx_type", "currency")
    search_fields = ("wallet__user__handle", "description")
    raw_id_fields = ("wallet", "escrow")
