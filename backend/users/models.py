from django.contrib.auth.models import AbstractUser
from django.db import models
from pgvector.django import HnswIndex, VectorField

from core.embeddings import EMBEDDING_DIMENSIONS
from core.validators import handle_validator, iso_alpha2


class UserRole(models.TextChoices):
    TALENT = "talent", "Talent"
    EMPLOYER = "employer", "Employer"


class UserTier(models.TextChoices):
    BASIC = "basic", "Basic"
    VERIFIED = "verified", "Verified"
    PRO = "pro", "Pro"


class KYCStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    PENDING = "pending", "Pending"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class User(AbstractUser):
    handle = models.CharField(
        max_length=30,
        unique=True,
        validators=[handle_validator],
        db_index=True,
    )
    role = models.CharField(max_length=16, choices=UserRole.choices, db_index=True)
    country_code = models.CharField(max_length=2, validators=[iso_alpha2], db_index=True)
    tier = models.CharField(
        max_length=16,
        choices=UserTier.choices,
        default=UserTier.BASIC,
    )
    kyc_status = models.CharField(
        max_length=16,
        choices=KYCStatus.choices,
        default=KYCStatus.UNVERIFIED,
        db_index=True,
    )
    verified_badge = models.BooleanField(
        default=False,
        help_text="Displayed when identity verification is complete.",
    )
    skill_tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Normalized English skill tags extracted from profile/resume.",
    )
    skill_embedding = VectorField(
        dimensions=EMBEDDING_DIMENSIONS,
        null=True,
        blank=True,
        help_text="Semantic embedding of normalized skills.",
    )

    class Meta:
        ordering = ["handle"]
        indexes = [
            HnswIndex(
                name="user_skill_emb_hnsw",
                fields=["skill_embedding"],
                opclasses=["vector_cosine_ops"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(kyc_status=KYCStatus.APPROVED)
                | models.Q(verified_badge=False),
                name="verified_badge_requires_approved_kyc",
            ),
        ]

    def __str__(self) -> str:
        return f"@{self.handle}"

    def save(self, *args, **kwargs):
        self.country_code = self.country_code.upper()
        if self.kyc_status != KYCStatus.APPROVED:
            self.verified_badge = False
        super().save(*args, **kwargs)


class EmergentSession(models.Model):
    """Session issued after Emergent-managed Google OAuth login."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="emergent_sessions",
    )
    session_token = models.CharField(max_length=512, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"EmergentSession({self.user.handle})"


class KYBStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class BusinessType(models.TextChoices):
    SOLE_PROP = "sole_prop", "Sole Proprietorship"
    LLC = "llc", "LLC"
    CORPORATION = "corporation", "Corporation"
    NONPROFIT = "nonprofit", "Non-profit"
    COOPERATIVE = "cooperative", "Cooperative"


class Entity(models.Model):
    """Business entity linked to an employer user (KYB)."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="entity",
    )
    kyb_status = models.CharField(
        max_length=16,
        choices=KYBStatus.choices,
        default=KYBStatus.UNVERIFIED,
        db_index=True,
    )
    business_type = models.CharField(
        max_length=32,
        choices=BusinessType.choices,
    )
    registration_no = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name_plural = "entities"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(kyb_status=KYBStatus.APPROVED)
                | ~models.Q(registration_no=""),
                name="approved_kyb_requires_registration_no",
            ),
        ]

    def __str__(self) -> str:
        return f"Entity({self.user.handle})"
