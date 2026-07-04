from django.urls import path

from verification.views import VerificationWebhookViewSet

webhook_list = VerificationWebhookViewSet.as_view({"post": "create"})

urlpatterns = [
    path("verification/webhook/", webhook_list, name="verification-webhook"),
]
