import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VerificationSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(db_index=True, max_length=32)),
                ("external_session_id", models.CharField(db_index=True, max_length=128, unique=True)),
                ("status", models.CharField(
                    choices=[
                        ("created", "Created"),
                        ("pending", "Pending"),
                        ("submitted", "Submitted"),
                        ("approved", "Approved"),
                        ("rejected", "Rejected"),
                    ],
                    db_index=True,
                    default="created",
                    max_length=16,
                )),
                ("redirect_url", models.URLField(blank=True, max_length=512)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="verification_sessions",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CountryVerificationBadge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("country_code", models.CharField(max_length=2)),
                ("label", models.CharField(help_text='Display label, e.g. "NG Verified".', max_length=32)),
                ("provider", models.CharField(max_length=32)),
                ("minted_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="country_badge",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-minted_at"]},
        ),
    ]
