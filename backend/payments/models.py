from django.db import models

from core.models import PaymentRail
from core.validators import iso_currency


class EscrowState(models.TextChoices):
    PENDING = "pending", "Pending funding"
    LOCKED = "locked", "Locked"
    RELEASED = "released", "Released"
    REFUNDED = "refunded", "Refunded"


class PaymentProvider(models.TextChoices):
    STRIPE = "stripe", "Stripe Connect"
    DLOCAL = "dlocal", "dLocal"


class TransactionType(models.TextChoices):
    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"
    ESCROW_LOCK = "escrow_lock", "Escrow lock"
    ESCROW_RELEASE = "escrow_release", "Escrow release"
    ESCROW_REFUND = "escrow_refund", "Escrow refund"
    PAYOUT = "payout", "Payout"


class Wallet(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    currency = models.CharField(max_length=3, validators=[iso_currency])
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    rail = models.CharField(max_length=32, choices=PaymentRail.choices)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="wallet_balance_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"Wallet({self.user.handle}, {self.currency})"

    def save(self, *args, **kwargs):
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)


class Escrow(models.Model):
    listing = models.OneToOneField(
        "jobs.Listing",
        on_delete=models.CASCADE,
        related_name="escrow",
    )
    employer = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="employer_escrows",
    )
    talent = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="talent_escrows",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, validators=[iso_currency])
    state = models.CharField(
        max_length=16,
        choices=EscrowState.choices,
        default=EscrowState.PENDING,
        db_index=True,
    )
    provider = models.CharField(
        max_length=16,
        choices=PaymentProvider.choices,
        blank=True,
    )
    provider_ref = models.CharField(max_length=128, blank=True, db_index=True)
    employer_signed_off = models.BooleanField(default=False)
    talent_signed_off = models.BooleanField(default=False)
    funded_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "escrows"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="escrow_amount_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"Escrow({self.listing.title}, {self.state})"

    def save(self, *args, **kwargs):
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)

    @property
    def both_signed_off(self) -> bool:
        return self.employer_signed_off and self.talent_signed_off


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    tx_type = models.CharField(max_length=20, choices=TransactionType.choices, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, validators=[iso_currency])
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)
    escrow = models.ForeignKey(
        Escrow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="wallet_tx_amount_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tx_type} {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)
