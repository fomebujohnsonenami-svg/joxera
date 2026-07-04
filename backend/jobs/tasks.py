import logging

from celery import shared_task
from django.db import transaction

from jobs.models import Listing
from jobs.services.skill_engine import (
    build_embedding_text,
    extract_skill_tags,
    generate_embedding,
)

logger = logging.getLogger(__name__)


@shared_task(name="jobs.parse_and_embed_listing", bind=True, max_retries=3)
def parse_and_embed_listing(self, listing_id: int) -> dict:
    """
    Universal skill translation pipeline:
    1. Send raw local-language description to Gemini via LangChain
    2. Extract normalized English skill tags
    3. Generate embedding vector and persist to pgvector
    """
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        logger.warning("Listing %s not found for embedding", listing_id)
        return {"status": "not_found", "listing_id": listing_id}

    try:
        extraction = extract_skill_tags(
            title=listing.title,
            description=listing.description,
            field=listing.field,
        )
        skill_tags: list[str] = extraction.get("normalized_skills", [])
        summary_en: str = extraction.get("summary_en", "")

        embed_text = build_embedding_text(
            title=listing.title,
            description=listing.description,
            field=listing.field,
            skill_tags=skill_tags,
            summary_en=summary_en,
        )
        embedding = generate_embedding(embed_text)

        with transaction.atomic():
            listing.skill_tags = skill_tags
            listing.skill_embedding = embedding
            listing.save(update_fields=["skill_tags", "skill_embedding", "updated_at"])

        logger.info(
            "Embedded listing %s — %d skills (lang=%s)",
            listing_id,
            len(skill_tags),
            extraction.get("detected_language", "?"),
        )
        return {
            "status": "ok",
            "listing_id": listing_id,
            "skill_count": len(skill_tags),
            "detected_language": extraction.get("detected_language"),
        }
    except Exception as exc:
        logger.exception("parse_and_embed_listing failed for %s", listing_id)
        raise self.retry(exc=exc, countdown=30 * (self.request.retries + 1))
