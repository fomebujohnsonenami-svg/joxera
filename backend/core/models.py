from django.db import models

from core.validators import iso_alpha2


class PaymentRail(models.TextChoices):
    MOBILE_MONEY = "MobileMoney", "Mobile Money"
    PIX = "Pix", "Pix"
    SEPA = "SEPA", "SEPA"
    ACH = "ACH", "ACH"
    UPI = "UPI", "UPI"
    SWIFT = "SWIFT", "SWIFT"
    CARD = "Card", "Card"


class CountryConfig(models.Model):
    """Regional parameters keyed by ISO 3166-1 alpha-2 country code."""

    country_code = models.CharField(
        max_length=2,
        unique=True,
        db_index=True,
        validators=[iso_alpha2],
        help_text="ISO 3166-1 alpha-2 country code",
    )
    country_name = models.CharField(max_length=100)
    currency = models.CharField(
        max_length=3,
        help_text="ISO 4217 currency code (e.g. USD, NGN, BRL)",
    )
    default_payment_rail = models.CharField(
        max_length=32,
        choices=PaymentRail.choices,
        help_text="Default payout rail for this region",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["country_code"]
        verbose_name = "Country configuration"
        verbose_name_plural = "Country configurations"

    def __str__(self) -> str:
        return f"{self.country_code} — {self.currency} / {self.default_payment_rail}"

    def save(self, *args, **kwargs):
        self.country_code = self.country_code.upper()
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)
