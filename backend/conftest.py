from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import PaymentRail
from jobs.models import Listing, ListingMode, ListingStatus, ListingTier
from payments.models import Escrow, EscrowState, Wallet
from users.models import KYCStatus, User, UserRole


@pytest.fixture(autouse=True)
def _disable_throttling(settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def employer(db):
    user = User.objects.create_user(
        username="employer1",
        email="employer@test.com",
        password="testpass123",
        handle="employer1",
        role=UserRole.EMPLOYER,
        country_code="US",
        kyc_status=KYCStatus.APPROVED,
        verified_badge=True,
    )
    return user


@pytest.fixture
def unverified_employer(db):
    return User.objects.create_user(
        username="unverified",
        email="unverified@test.com",
        password="testpass123",
        handle="unverified",
        role=UserRole.EMPLOYER,
        country_code="US",
        kyc_status=KYCStatus.UNVERIFIED,
    )


@pytest.fixture
def talent(db):
    user = User.objects.create_user(
        username="talent1",
        email="talent@test.com",
        password="testpass123",
        handle="talent1",
        role=UserRole.TALENT,
        country_code="US",
        kyc_status=KYCStatus.APPROVED,
        verified_badge=True,
    )
    return user


@pytest.fixture
def remote_listing(employer):
    return Listing.objects.create(
        owner=employer,
        title="Backend Developer",
        description="Build APIs with Django.",
        field="backend-dev",
        tier=ListingTier.STANDARD,
        mode=ListingMode.REMOTE,
        country_code="US",
        currency="USD",
        budget=Decimal("5000.00"),
        status=ListingStatus.PUBLISHED,
    )


@pytest.fixture
def employer_wallet(employer):
    return Wallet.objects.create(
        user=employer,
        currency="USD",
        balance=Decimal("10000.00"),
        rail=PaymentRail.ACH,
    )


@pytest.fixture
def talent_wallet(talent):
    return Wallet.objects.create(
        user=talent,
        currency="USD",
        balance=Decimal("0.00"),
        rail=PaymentRail.ACH,
    )


@pytest.fixture
def funded_escrow(remote_listing, employer, talent, employer_wallet):
    from payments.services.escrow import create_escrow_for_listing, lock_escrow_from_wallet

    escrow = create_escrow_for_listing(remote_listing, employer, talent=talent)
    lock_escrow_from_wallet(escrow.id, employer)
    return Escrow.objects.get(pk=escrow.id)


@pytest.fixture
def auth_client(api_client):
    def _authenticate(user):
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return api_client
    return _authenticate
