from django.db import models

from core.validators import iso_alpha2


class VerificationSession(models.Model):
    """Tracks an in-flight KYC session with an external identity provider."""

    class SessionStatus(models.TextChoices):
        CREATED = "created", "Created"
        PENDING = "pending", "Pending"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="verification_sessions",
    )
    provider = models.CharField(max_length=32, db_index=True)
    external_session_id = models.CharField(max_length=128, unique=True, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=SessionStatus.choices,
        default=SessionStatus.CREATED,
        db_index=True,
    )
    redirect_url = models.URLField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.external_session_id} ({self.status})"


class CountryVerificationBadge(models.Model):
    """
    Minted proof-of-identity badge: flag + 'XX Verified'.
    One badge per user, tied to their verified country.
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="country_badge",
    )
    country_code = models.CharField(max_length=2, validators=[iso_alpha2])
    label = models.CharField(
        max_length=32,
        help_text='Display label, e.g. "NG Verified".',
    )
    provider = models.CharField(max_length=32)
    minted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-minted_at"]

    def __str__(self) -> str:
        return f"{self.label} (@{self.user.handle})"

    def save(self, *args, **kwargs):
        self.country_code = self.country_code.upper()
        if not self.label:
            self.label = f"{self.country_code} Verified"
        super().save(*args, **kwargs)
