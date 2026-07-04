from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from django.db.models import Q
from pgvector.django import HnswIndex, VectorField

from core.embeddings import EMBEDDING_DIMENSIONS
from core.validators import iso_alpha2, iso_currency


class ListingMode(models.TextChoices):
    REMOTE = "remote", "Remote"
    ONSITE = "onsite", "On-site"
    HYBRID = "hybrid", "Hybrid"


class ListingStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    CLOSED = "closed", "Closed"
    FILLED = "filled", "Filled"
    CANCELLED = "cancelled", "Cancelled"


class ListingTier(models.TextChoices):
    STANDARD = "standard", "Standard"
    PRIORITY = "priority", "Priority"
    ENTERPRISE = "enterprise", "Enterprise"


class Listing(models.Model):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="listings",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    field = models.CharField(
        max_length=64,
        help_text="Domain or trade field (e.g. plumbing, backend-dev).",
        db_index=True,
    )
    tier = models.CharField(
        max_length=16,
        choices=ListingTier.choices,
        default=ListingTier.STANDARD,
    )
    mode = models.CharField(max_length=16, choices=ListingMode.choices, db_index=True)
    country_code = models.CharField(max_length=2, validators=[iso_alpha2], db_index=True)
    geo_point = models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
        help_text="WGS-84 point for on-site/hybrid jobs; null for fully remote.",
    )
    currency = models.CharField(max_length=3, validators=[iso_currency])
    budget = models.DecimalField(max_digits=14, decimal_places=2)
    escrow_id = models.CharField(max_length=64, blank=True, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=ListingStatus.choices,
        default=ListingStatus.DRAFT,
        db_index=True,
    )
    skill_tags = models.JSONField(
        default=list,
        blank=True,
        help_text="LLM-normalized skill tags (English) extracted from description.",
    )
    skill_embedding = VectorField(
        dimensions=EMBEDDING_DIMENSIONS,
        null=True,
        blank=True,
        help_text="Semantic embedding of title + normalized skills.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            GistIndex(fields=["geo_point"], name="listing_geo_point_gist"),
            models.Index(fields=["country_code", "status"], name="listing_country_status_idx"),
            HnswIndex(
                name="listing_skill_emb_hnsw",
                fields=["skill_embedding"],
                opclasses=["vector_cosine_ops"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(budget__gt=0),
                name="listing_budget_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(mode=ListingMode.REMOTE, geo_point__isnull=True)
                    | ~Q(mode=ListingMode.REMOTE)
                ),
                name="remote_listing_no_geo_point",
            ),
            models.CheckConstraint(
                condition=(
                    Q(mode=ListingMode.REMOTE)
                    | Q(mode=ListingMode.HYBRID, geo_point__isnull=False)
                    | Q(mode=ListingMode.ONSITE, geo_point__isnull=False)
                ),
                name="onsite_hybrid_requires_geo_point",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.country_code = self.country_code.upper()
        self.currency = self.currency.upper()
        super().save(*args, **kwargs)


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    REVIEWING = "reviewing", "Reviewing"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"


class Application(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    talent = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=16,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        db_index=True,
    )
    cover_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "talent"],
                name="unique_application_per_listing_talent",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.talent.handle} → {self.listing.title}"
