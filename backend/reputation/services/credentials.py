"""
Mint signed proof-of-work credentials when escrow is released.
"""

from __future__ import annotations

import logging

from django.utils import timezone

from core.signing import sign_payload
from payments.models import Escrow
from reputation.models import Reference

logger = logging.getLogger(__name__)


def build_pow_payload(escrow: Escrow) -> dict:
    listing = escrow.listing
    return {
        "user_id": escrow.talent_id,
        "listing_id": listing.id,
        "field": listing.field,
        "tier": listing.tier,
        "employer_id": escrow.employer_id,
        "timestamp": (escrow.released_at or timezone.now()).isoformat(),
    }


def issue_proof_of_work(escrow: Escrow) -> Reference | None:
    """
    Generate and persist a signed proof-of-work record for the talent.
    Idempotent — returns existing reference if already minted.
    """
    if not escrow.talent_id:
        logger.warning("Skipping PoW mint — escrow %s has no talent", escrow.id)
        return None

    existing = Reference.objects.filter(user_id=escrow.talent_id, listing_id=escrow.listing_id).first()
    if existing:
        return existing

    escrow = Escrow.objects.select_related("listing", "talent", "employer").get(pk=escrow.pk)
    payload = build_pow_payload(escrow)
    sig_hash, sig_b64, stored_payload = sign_payload(payload)

    reference = Reference.objects.create(
        user_id=escrow.talent_id,
        listing_id=escrow.listing_id,
        signed_proof=stored_payload,
        signature_hash=sig_hash,
        signature_b64=sig_b64,
    )
    logger.info(
        "Minted proof-of-work reference %s for @%s — listing %s",
        reference.id,
        escrow.talent.handle,
        escrow.listing.title,
    )
    return reference
