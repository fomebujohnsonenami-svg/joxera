import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Escrow, EscrowState

from .services.credentials import issue_proof_of_work

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Escrow)
def mint_proof_on_escrow_release(sender, instance: Escrow, **kwargs) -> None:
    """Hook: escrow RELEASE → cryptographically signed proof-of-work."""
    if instance.state != EscrowState.RELEASED:
        return
    if not instance.talent_id:
        return
    try:
        issue_proof_of_work(instance)
    except Exception:
        logger.exception("Failed to mint proof-of-work for escrow %s", instance.id)
