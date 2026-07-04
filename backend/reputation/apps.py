from django.apps import AppConfig


class ReputationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reputation"
    verbose_name = "Reputation & Credentials"

    def ready(self) -> None:
        import reputation.signals  # noqa: F401
