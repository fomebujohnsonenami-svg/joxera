from django.db import models


class Reference(models.Model):
    """Cryptographically signed proof-of-work credential issued on escrow release."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="references",
    )
    listing = models.ForeignKey(
        "jobs.Listing",
        on_delete=models.CASCADE,
        related_name="references",
    )
    signed_proof = models.JSONField(
        help_text="Canonical signed payload: user_id, listing_id, field, tier, employer_id, timestamp.",
    )
    signature_hash = models.CharField(max_length=128, unique=True, db_index=True)
    signature_b64 = models.CharField(
        max_length=128,
        help_text="Detached Ed25519 signature (base64).",
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "listing"],
                name="unique_reference_per_user_listing",
            ),
        ]

    def __str__(self) -> str:
        return f"Reference({self.user.handle}, {self.listing.title})"
