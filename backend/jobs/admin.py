from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Application, Listing


@admin.register(Listing)
class ListingAdmin(GISModelAdmin):
    list_display = ("title", "owner", "mode", "country_code", "budget", "currency", "status")
    list_filter = ("mode", "status", "tier", "country_code", "field")
    search_fields = ("title", "owner__handle", "field")
    raw_id_fields = ("owner",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("listing", "talent", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("listing__title", "talent__handle")
    raw_id_fields = ("listing", "talent")
