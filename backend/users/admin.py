from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Entity, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "handle",
        "username",
        "email",
        "role",
        "country_code",
        "tier",
        "kyc_status",
        "verified_badge",
        "is_staff",
    )
    list_filter = ("role", "tier", "kyc_status", "verified_badge", "country_code")
    search_fields = ("handle", "username", "email")
    ordering = ("handle",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Joxera profile",
            {
                "fields": (
                    "handle",
                    "role",
                    "country_code",
                    "tier",
                    "kyc_status",
                    "verified_badge",
                ),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Joxera profile",
            {
                "fields": ("handle", "role", "country_code"),
            },
        ),
    )


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("user", "kyb_status", "business_type", "registration_no")
    list_filter = ("kyb_status", "business_type")
    search_fields = ("user__handle", "registration_no")
