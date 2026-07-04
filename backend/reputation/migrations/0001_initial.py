import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("jobs", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Reference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("signed_proof", models.JSONField(help_text="Canonical signed payload: user_id, listing_id, field, tier, employer_id, timestamp.")),
                ("signature_hash", models.CharField(db_index=True, max_length=128, unique=True)),
                ("signature_b64", models.CharField(help_text="Detached Ed25519 signature (base64).", max_length=128)),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("listing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="references", to="jobs.listing")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="references", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-issued_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="reference",
            constraint=models.UniqueConstraint(fields=("user", "listing"), name="unique_reference_per_user_listing"),
        ),
    ]
