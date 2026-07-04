import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import KYCStatus, User

from .models import CountryVerificationBadge

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def mint_country_verification_badge(sender, instance: User, **kwargs):
    """
    On KYC approval, mint a Country Verification Badge (flag + 'XX Verified')
    and flip verified_badge on the user profile.
    """
    if instance.kyc_status != KYCStatus.APPROVED:
        return

    badge, created = CountryVerificationBadge.objects.get_or_create(
        user=instance,
        defaults={
            "country_code": instance.country_code,
            "label": f"{instance.country_code} Verified",
            "provider": _latest_provider(instance),
        },
    )

    if not created and badge.country_code != instance.country_code:
        badge.country_code = instance.country_code
        badge.label = f"{instance.country_code} Verified"
        badge.save(update_fields=["country_code", "label"])

    if not instance.verified_badge:
        User.objects.filter(pk=instance.pk).update(verified_badge=True)
        logger.info("Minted country badge '%s' for user %s", badge.label, instance.pk)


def _latest_provider(user: User) -> str:
    session = user.verification_sessions.order_by("-created_at").first()
    return session.provider if session else "unknown"
