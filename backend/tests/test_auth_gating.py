import pytest
from rest_framework import status

from jobs.models import ListingMode, ListingStatus, ListingTier


@pytest.mark.django_db
class TestAuthGating:
    def test_unverified_employer_cannot_post_listing(self, api_client, unverified_employer, auth_client):
        client = auth_client(unverified_employer)
        response = client.post(
            "/api/listings/",
            {
                "title": "Blocked Job",
                "description": "Should fail KYC gate.",
                "field": "plumbing",
                "tier": ListingTier.STANDARD,
                "mode": ListingMode.REMOTE,
                "country_code": "US",
                "currency": "USD",
                "budget": "100.00",
                "status": ListingStatus.PUBLISHED,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verified_employer_can_post_listing(self, api_client, employer, auth_client):
        client = auth_client(employer)
        response = client.post(
            "/api/listings/",
            {
                "title": "Verified Job",
                "description": "KYC approved.",
                "field": "plumbing",
                "tier": ListingTier.STANDARD,
                "mode": ListingMode.REMOTE,
                "country_code": "US",
                "currency": "USD",
                "budget": "250.00",
                "status": ListingStatus.PUBLISHED,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_anonymous_cannot_post_listing(self, api_client):
        response = api_client.post(
            "/api/listings/",
            {"title": "Anon"},
            format="json",
        )
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_register_and_kyc_simulate(self, api_client, settings):
        settings.DEBUG = True
        reg = api_client.post(
            "/api/auth/register/",
            {
                "email": "new@test.com",
                "password": "securepass123",
                "handle": "newuser",
                "country": "US",
                "role": "employer",
            },
            format="json",
        )
        assert reg.status_code == status.HTTP_201_CREATED
        token = reg.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        approve = api_client.post("/api/auth/kyc/simulate-approve/")
        assert approve.status_code == status.HTTP_200_OK
        assert approve.data["isVerified"] is True
