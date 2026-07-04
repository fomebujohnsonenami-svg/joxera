from django.contrib import admin

from .models import Reference


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "signature_hash", "issued_at")
    search_fields = ("user__handle", "listing__title", "signature_hash")
    raw_id_fields = ("user", "listing")
    readonly_fields = ("signature_hash", "signature_b64", "signed_proof", "issued_at")
