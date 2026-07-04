from django.contrib import admin

from .models import CountryVerificationBadge, VerificationSession


@admin.register(VerificationSession)
class VerificationSessionAdmin(admin.ModelAdmin):
    list_display = ("external_session_id", "user", "provider", "status", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("external_session_id", "user__handle")
    raw_id_fields = ("user",)


@admin.register(CountryVerificationBadge)
class CountryVerificationBadgeAdmin(admin.ModelAdmin):
    list_display = ("label", "user", "country_code", "provider", "minted_at")
    search_fields = ("user__handle", "label", "country_code")
    raw_id_fields = ("user",)
