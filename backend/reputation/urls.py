from django.urls import path

from .views import PublicKeyView, VerifyReferenceView

urlpatterns = [
    path(
        "references/verify/<int:reference_id>/",
        VerifyReferenceView.as_view(),
        name="references-verify",
    ),
    path(
        "references/verify/",
        VerifyReferenceView.as_view(),
        name="references-verify-hash",
    ),
    path(
        "references/public-key/",
        PublicKeyView.as_view(),
        name="references-public-key",
    ),
]
