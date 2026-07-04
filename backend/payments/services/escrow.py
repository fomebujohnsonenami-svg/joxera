"""
Atomic escrow state transitions — all wallet mutations run inside
select_for_update() + transaction.atomic() to prevent double-spend.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.models import CountryConfig, PaymentRail
from jobs.models import Application, ApplicationStatus, Listing
from users.models import User

from payments.models import (
    Escrow,
    EscrowState,
    PaymentProvider,
    TransactionType,
    Wallet,
    WalletTransaction,
)

logger = logging.getLogger(__name__)


class EscrowError(Exception):
    pass


class InsufficientFundsError(EscrowError):
    pass


class InvalidEscrowStateError(EscrowError):
    pass


def _provider_for_rail(rail: str) -> str:
    if rail in (PaymentRail.PIX, PaymentRail.MOBILE_MONEY):
        return PaymentProvider.DLOCAL
    return PaymentProvider.STRIPE


def get_or_create_wallet(user: User, currency: str | None = None) -> Wallet:
    currency = (currency or _default_currency(user)).upper()
    rail = _default_rail(user)
    wallet, _ = Wallet.objects.get_or_create(
        user=user,
        defaults={"currency": currency, "rail": rail, "balance": Decimal("0")},
    )
    return wallet


def _default_currency(user: User) -> str:
    config = CountryConfig.objects.filter(country_code=user.country_code).first()
    return config.currency if config else "USD"


def _default_rail(user: User) -> str:
    config = CountryConfig.objects.filter(country_code=user.country_code).first()
    return config.default_payment_rail if config else PaymentRail.CARD


def _record_transaction(
    wallet: Wallet,
    tx_type: str,
    amount: Decimal,
    balance_after: Decimal,
    *,
    escrow: Escrow | None = None,
    description: str = "",
    metadata: dict | None = None,
) -> WalletTransaction:
    return WalletTransaction.objects.create(
        wallet=wallet,
        tx_type=tx_type,
        amount=amount,
        currency=wallet.currency,
        balance_after=balance_after,
        escrow=escrow,
        description=description,
        metadata=metadata or {},
    )


@transaction.atomic
def create_escrow_for_listing(
    listing: Listing,
    employer: User,
    talent: User | None = None,
    provider: str = "",
) -> Escrow:
    if hasattr(listing, "escrow"):
        raise EscrowError("Listing already has an escrow.")

    escrow = Escrow.objects.create(
        listing=listing,
        employer=employer,
        talent=talent,
        amount=listing.budget,
        currency=listing.currency,
        state=EscrowState.PENDING,
        provider=provider or _provider_for_rail(_default_rail(employer)),
    )
    listing.escrow_id = str(escrow.id)
    listing.save(update_fields=["escrow_id"])
    return escrow


@transaction.atomic
def lock_escrow_from_wallet(escrow_id: int, employer: User) -> Escrow:
    """Employer funds escrow from wallet balance → LOCKED."""
    escrow = Escrow.objects.select_for_update().get(pk=escrow_id)
    if escrow.employer_id != employer.id:
        raise EscrowError("Only the employer may fund this escrow.")
    if escrow.state != EscrowState.PENDING:
        raise InvalidEscrowStateError(f"Cannot fund escrow in state '{escrow.state}'.")

    wallet = Wallet.objects.select_for_update().get(user=employer)
    if wallet.currency != escrow.currency:
        raise EscrowError("Wallet currency does not match escrow currency.")
    if wallet.balance < escrow.amount:
        raise InsufficientFundsError(
            f"Need {escrow.amount} {escrow.currency}, have {wallet.balance}."
        )

    wallet.balance -= escrow.amount
    wallet.save(update_fields=["balance", "updated_at"])

    _record_transaction(
        wallet,
        TransactionType.ESCROW_LOCK,
        escrow.amount,
        wallet.balance,
        escrow=escrow,
        description=f"Escrow locked for {escrow.listing.title}",
    )

    escrow.state = EscrowState.LOCKED
    escrow.funded_at = timezone.now()
    escrow.save(update_fields=["state", "funded_at", "updated_at"])
    return escrow


@transaction.atomic
def lock_escrow_from_provider(escrow_id: int, provider_ref: str) -> Escrow:
    """Webhook confirms external payment → LOCKED."""
    escrow = Escrow.objects.select_for_update().get(pk=escrow_id)
    if escrow.state != EscrowState.PENDING:
        raise InvalidEscrowStateError(f"Escrow {escrow_id} is not pending (state={escrow.state}).")

    escrow.state = EscrowState.LOCKED
    escrow.provider_ref = provider_ref
    escrow.funded_at = timezone.now()
    escrow.save(update_fields=["state", "provider_ref", "funded_at", "updated_at"])
    logger.info("Escrow %s locked via provider ref %s", escrow_id, provider_ref)
    return escrow


@transaction.atomic
def sign_off_escrow(escrow_id: int, user: User) -> Escrow:
    """Record employer or talent sign-off on completed work."""
    escrow = Escrow.objects.select_for_update().get(pk=escrow_id)

    if escrow.state != EscrowState.LOCKED:
        raise InvalidEscrowStateError(
            f"Sign-off only allowed when escrow is locked (current: {escrow.state})."
        )

    if user.id == escrow.employer_id:
        escrow.employer_signed_off = True
    elif escrow.talent_id and user.id == escrow.talent_id:
        escrow.talent_signed_off = True
    else:
        raise EscrowError("You are not a party to this escrow.")

    escrow.save(update_fields=["employer_signed_off", "talent_signed_off", "updated_at"])
    return escrow


@transaction.atomic
def release_escrow(escrow_id: int) -> Escrow:
    """
    RELEASED → credit talent wallet.
    Requires both parties signed off; idempotent on already-released escrows.
    """
    escrow = Escrow.objects.select_for_update().select_related("listing", "talent").get(pk=escrow_id)

    if escrow.state == EscrowState.RELEASED:
        return escrow
    if escrow.state != EscrowState.LOCKED:
        raise InvalidEscrowStateError(f"Cannot release escrow in state '{escrow.state}'.")
    if not escrow.both_signed_off:
        raise EscrowError("Both employer and talent must sign off before release.")
    if not escrow.talent_id:
        raise EscrowError("Escrow has no assigned talent.")

    talent_wallet = Wallet.objects.select_for_update().get(user_id=escrow.talent_id)
    if talent_wallet.currency != escrow.currency:
        raise EscrowError("Talent wallet currency mismatch.")

    talent_wallet.balance += escrow.amount
    talent_wallet.save(update_fields=["balance", "updated_at"])

    _record_transaction(
        talent_wallet,
        TransactionType.ESCROW_RELEASE,
        escrow.amount,
        talent_wallet.balance,
        escrow=escrow,
        description=f"Escrow released for {escrow.listing.title}",
    )

    escrow.state = EscrowState.RELEASED
    escrow.released_at = timezone.now()
    escrow.save(update_fields=["state", "released_at", "updated_at"])
    logger.info("Escrow %s released — %s %s to talent %s", escrow_id, escrow.amount, escrow.currency, escrow.talent_id)
    return escrow


@transaction.atomic
def refund_escrow(escrow_id: int, employer: User) -> Escrow:
    """Refund locked escrow back to employer wallet."""
    escrow = Escrow.objects.select_for_update().get(pk=escrow_id)
    if escrow.employer_id != employer.id:
        raise EscrowError("Only the employer may request a refund.")
    if escrow.state != EscrowState.LOCKED:
        raise InvalidEscrowStateError(f"Cannot refund escrow in state '{escrow.state}'.")

    wallet = Wallet.objects.select_for_update().get(user=employer)
    wallet.balance += escrow.amount
    wallet.save(update_fields=["balance", "updated_at"])

    _record_transaction(
        wallet,
        TransactionType.ESCROW_REFUND,
        escrow.amount,
        wallet.balance,
        escrow=escrow,
        description=f"Escrow refunded for {escrow.listing.title}",
    )

    escrow.state = EscrowState.REFUNDED
    escrow.save(update_fields=["state", "updated_at"])
    return escrow


def assign_talent_from_application(escrow: Escrow, application: Application) -> Escrow:
    if application.status != ApplicationStatus.ACCEPTED:
        raise EscrowError("Application must be accepted before assigning talent.")
    escrow.talent = application.talent
    escrow.save(update_fields=["talent", "updated_at"])
    return escrow
