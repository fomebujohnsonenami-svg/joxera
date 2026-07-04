from django.db import migrations, models


SEED_COUNTRIES = [
    ("US", "United States", "USD", "ACH"),
    ("GB", "United Kingdom", "GBP", "SEPA"),
    ("CA", "Canada", "CAD", "ACH"),
    ("DE", "Germany", "EUR", "SEPA"),
    ("FR", "France", "EUR", "SEPA"),
    ("NG", "Nigeria", "NGN", "MobileMoney"),
    ("KE", "Kenya", "KES", "MobileMoney"),
    ("GH", "Ghana", "GHS", "MobileMoney"),
    ("IN", "India", "INR", "UPI"),
    ("BR", "Brazil", "BRL", "Pix"),
    ("MX", "Mexico", "MXN", "Card"),
    ("AU", "Australia", "AUD", "SWIFT"),
    ("JP", "Japan", "JPY", "SWIFT"),
    ("ZA", "South Africa", "ZAR", "MobileMoney"),
    ("PH", "Philippines", "PHP", "MobileMoney"),
]


def seed_country_configs(apps, schema_editor):
    CountryConfig = apps.get_model("core", "CountryConfig")
    for code, name, currency, rail in SEED_COUNTRIES:
        CountryConfig.objects.get_or_create(
            country_code=code,
            defaults={
                "country_name": name,
                "currency": currency,
                "default_payment_rail": rail,
                "is_active": True,
            },
        )


def unseed_country_configs(apps, schema_editor):
    CountryConfig = apps.get_model("core", "CountryConfig")
    codes = [row[0] for row in SEED_COUNTRIES]
    CountryConfig.objects.filter(country_code__in=codes).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CountryConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "country_code",
                    models.CharField(
                        db_index=True,
                        help_text="ISO 3166-1 alpha-2 country code",
                        max_length=2,
                        unique=True,
                    ),
                ),
                ("country_name", models.CharField(max_length=100)),
                (
                    "currency",
                    models.CharField(
                        help_text="ISO 4217 currency code (e.g. USD, NGN, BRL)",
                        max_length=3,
                    ),
                ),
                (
                    "default_payment_rail",
                    models.CharField(
                        choices=[
                            ("MobileMoney", "Mobile Money"),
                            ("Pix", "Pix"),
                            ("SEPA", "SEPA"),
                            ("ACH", "ACH"),
                            ("UPI", "UPI"),
                            ("SWIFT", "SWIFT"),
                            ("Card", "Card"),
                        ],
                        help_text="Default payout rail for this region",
                        max_length=32,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Country configuration",
                "verbose_name_plural": "Country configurations",
                "ordering": ["country_code"],
            },
        ),
        migrations.RunPython(seed_country_configs, unseed_country_configs),
    ]
