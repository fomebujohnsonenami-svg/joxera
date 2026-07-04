from django.core.validators import RegexValidator

iso_alpha2 = RegexValidator(
    regex=r"^[A-Z]{2}$",
    message="Country code must be ISO 3166-1 alpha-2 (e.g. US, NG).",
)

iso_currency = RegexValidator(
    regex=r"^[A-Z]{3}$",
    message="Currency must be ISO 4217 (e.g. USD, NGN).",
)

handle_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_]{3,30}$",
    message="Handle must be 3–30 alphanumeric characters or underscores.",
)
