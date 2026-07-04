from decimal import Decimal

import pytest
from django.db import connection

from payments.models import EscrowState, Wallet, WalletTransaction
from payments.services.escrow import (
    InsufficientFundsError,
    InvalidEscrowStateError,
    create_escrow_for_listing,
    lock_escrow_from_wallet,
    refund_escrow,
    release_escrow,
    sign_off_escrow,
)


@pytest.mark.django_db
class TestEscrowAtomicTransitions:
    def test_lock_deducts_employer_wallet(self, remote_listing, employer, employer_wallet):
        escrow = create_escrow_for_listing(remote_listing, employer)
        lock_escrow_from_wallet(escrow.id, employer)

        employer_wallet.refresh_from_db()
        escrow.refresh_from_db()
        assert escrow.state == EscrowState.LOCKED
        assert employer_wallet.balance == Decimal("5000.00")
        assert WalletTransaction.objects.filter(tx_type="escrow_lock").count() == 1

    def test_lock_rejects_insufficient_funds(self, remote_listing, employer):
        Wallet.objects.create(
            user=employer, currency="USD", balance=Decimal("10.00"), rail="ACH"
        )
        escrow = create_escrow_for_listing(remote_listing, employer)
        with pytest.raises(InsufficientFundsError):
            lock_escrow_from_wallet(escrow.id, employer)

    def test_release_requires_both_signoffs(self, funded_escrow, employer, talent):
        from payments.services.escrow import EscrowError

        with pytest.raises(EscrowError):
            release_escrow(funded_escrow.id)

    def test_release_credits_talent_once(self, funded_escrow, employer, talent, talent_wallet):
        sign_off_escrow(funded_escrow.id, employer)
        sign_off_escrow(funded_escrow.id, talent)

        release_escrow(funded_escrow.id)
        talent_wallet.refresh_from_db()
        assert talent_wallet.balance == Decimal("5000.00")

        # Idempotent second release must not double-credit
        release_escrow(funded_escrow.id)
        talent_wallet.refresh_from_db()
        assert talent_wallet.balance == Decimal("5000.00")

    def test_refund_returns_funds_to_employer(self, funded_escrow, employer, employer_wallet):
        refund_escrow(funded_escrow.id, employer)
        employer_wallet.refresh_from_db()
        assert employer_wallet.balance == Decimal("10000.00")

    def test_cannot_release_refunded_escrow(self, funded_escrow, employer, talent):
        refund_escrow(funded_escrow.id, employer)
        sign_off_escrow(funded_escrow.id, employer)
        sign_off_escrow(funded_escrow.id, talent)
        with pytest.raises(InvalidEscrowStateError):
            release_escrow(funded_escrow.id)

    def test_concurrent_release_no_double_spend(self, funded_escrow, employer, talent, talent_wallet):
        sign_off_escrow(funded_escrow.id, employer)
        sign_off_escrow(funded_escrow.id, talent)

        release_escrow(funded_escrow.id)
        release_escrow(funded_escrow.id)

        talent_wallet.refresh_from_db()
        release_count = WalletTransaction.objects.filter(
            wallet=talent_wallet, tx_type="escrow_release"
        ).count()
        assert release_count == 1
        assert talent_wallet.balance == Decimal("5000.00")
