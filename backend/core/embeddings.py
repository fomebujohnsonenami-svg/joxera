"""Shared embedding configuration for skill matching."""

from django.conf import settings

EMBEDDING_DIMENSIONS: int = getattr(settings, "SKILL_EMBEDDING_DIMENSIONS", 768)
