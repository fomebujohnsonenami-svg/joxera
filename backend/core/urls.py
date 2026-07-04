from django.urls import include, path

from . import views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("v3/global/config/", views.global_config, name="global-config"),
    path("v3/global/", include("verification.urls")),
    path("v3/global/", include("payments.urls")),
    path("v3/global/", include("reputation.urls")),
    path("", include("jobs.urls")),
    path("", include("users.urls")),
]
