import logging

from payments.models import TransactionType, WalletTransaction
from payments.services.escrow import lock_escrow_from_provider

logger = logging.getLogger(__name__)


def handle_settlement_event(event) -> dict:
    """Apply a normalized Stripe/dLocal settlement webhook."""
    if event.status in ("funded", "paid", "completed") and event.escrow_ref:
        try:
            escrow_id = int(event.escrow_ref)
        except (TypeError, ValueError):
            logger.warning("Invalid escrow_ref in webhook: %s", event.escrow_ref)
            return {"status": "ignored", "reason": "invalid_escrow_ref"}

        if event.event_type.startswith("payment") or "payment_intent.succeeded" in event.event_type:
            escrow = lock_escrow_from_provider(escrow_id, event.provider_ref)
            return {"status": "locked", "escrow_id": escrow.id}

    if event.status == "paid" and event.provider_ref:
        tx = WalletTransaction.objects.filter(
            metadata__provider_ref=event.provider_ref,
            tx_type=TransactionType.PAYOUT,
        ).first()
        if tx:
            tx.metadata = {**tx.metadata, "settlement_status": "paid"}
            tx.save(update_fields=["metadata"])
            return {"status": "payout_confirmed", "transaction_id": tx.id}

    return {"status": "ignored", "event_type": event.event_type}
