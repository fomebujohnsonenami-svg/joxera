"""Inclusive multi-tier job taxonomy — fields span corporate tech to local trades."""

from django.db import models


class JobField(models.TextChoices):
    SKILLED_TRADES = "skilled_trades", "Skilled Trades"
    TECHNOLOGY = "technology", "Technology"
    HEALTHCARE = "healthcare", "Healthcare"
    LOGISTICS = "logistics", "Logistics & Delivery"
    HOSPITALITY = "hospitality", "Hospitality"
    CREATIVE = "creative", "Creative & Design"
    EDUCATION = "education", "Education & Training"
    AGRICULTURE = "agriculture", "Agriculture"
    COMMUNITY = "community", "Community & Gig"
    OTHER = "other", "Other"


# Tier → typical poster profile (used by frontend dynamic forms)
TIER_POSTER_PROFILE = {
    "standard": "community",
    "priority": "community",
    "enterprise": "enterprise",
}
