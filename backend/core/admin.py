from django.contrib import admin

from .models import CountryConfig


@admin.register(CountryConfig)
class CountryConfigAdmin(admin.ModelAdmin):
    list_display = (
        "country_code",
        "country_name",
        "currency",
        "default_payment_rail",
        "is_active",
        "updated_at",
    )
    list_filter = ("default_payment_rail", "is_active", "currency")
    search_fields = ("country_code", "country_name")
    ordering = ("country_code",)
