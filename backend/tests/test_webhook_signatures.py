import hashlib
import hmac
import json

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

from payments.providers.dlocal import DLocalProvider
from payments.providers.stripe_connect import StripeConnectProvider


@pytest.mark.django_db
class TestWebhookSignatureValidation:
    def test_payment_webhook_rejects_invalid_stripe_signature(self, api_client, settings):
        settings.STRIPE_WEBHOOK_SECRET = "whsec_test_secret"
        payload = {"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}}
        response = api_client.post(
            "/api/v3/global/payments/webhook/?provider=stripe",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_payment_webhook_rejects_missing_dlocal_secret(self, api_client, settings):
        settings.DLOCAL_WEBHOOK_SECRET = ""
        provider = DLocalProvider()
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v3/global/payments/webhook/?provider=dlocal",
            data=json.dumps({"status": "PAID", "id": "pay_1"}),
            content_type="application/json",
        )
        assert provider.verify_webhook_signature(request) is False

    @override_settings(DLOCAL_WEBHOOK_SECRET="test-dlocal-secret")
    def test_dlocal_valid_hmac_accepted(self):
        provider = DLocalProvider()
        body = json.dumps({"status": "PAID", "metadata": {"escrow_id": "1"}}).encode()
        sig = hmac.new(b"test-dlocal-secret", body, hashlib.sha256).hexdigest()
        factory = APIRequestFactory()
        request = factory.post(
            "/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE=sig,
        )
        assert provider.verify_webhook_signature(request) is True

    def test_verification_webhook_rejects_invalid_persona_hmac(self, api_client, settings):
        settings.PERSONA_WEBHOOK_SECRET = "persona-test-secret"
        payload = {"data": {"attributes": {"status": "approved"}}}
        response = api_client.post(
            "/api/v3/global/verification/webhook/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_PERSONA_SIGNATURE="bad-signature",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_stripe_provider_rejects_empty_signature(self, settings):
        settings.STRIPE_WEBHOOK_SECRET = "whsec_test"
        provider = StripeConnectProvider()
        factory = APIRequestFactory()
        request = factory.post("/", data=b"{}", content_type="application/json")
        assert provider.verify_webhook_signature(request) is False
