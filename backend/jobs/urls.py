from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApplicationViewSet,
    CountryJobFeedView,
    JobMatchView,
    ListingViewSet,
    NearbyJobsView,
)

router = DefaultRouter()
router.register(r"listings", ListingViewSet, basename="listing")
router.register(r"applications", ApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
    path("v3/global/jobs/nearby/", NearbyJobsView.as_view(), name="jobs-nearby"),
    path("v3/global/jobs/match/", JobMatchView.as_view(), name="jobs-match"),
    path(
        "countries/<str:country_code>/jobs/",
        CountryJobFeedView.as_view(),
        name="country-jobs",
    ),
]
