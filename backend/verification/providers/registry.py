from django.conf import settings

from .base import IdentityProvider
from .persona import PersonaProvider
from .veriff import VeriffProvider

_PROVIDERS: dict[str, type[IdentityProvider]] = {
    "persona": PersonaProvider,
    "veriff": VeriffProvider,
}


def get_identity_provider() -> IdentityProvider:
    name = getattr(settings, "IDENTITY_PROVIDER", "persona").lower()
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown IDENTITY_PROVIDER '{name}'. "
            f"Choose from: {', '.join(_PROVIDERS)}"
        )
    return provider_cls()
