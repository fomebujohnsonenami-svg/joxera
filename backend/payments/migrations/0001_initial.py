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
            name="Wallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("currency", models.CharField(max_length=3)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("rail", models.CharField(choices=[("MobileMoney", "Mobile Money"), ("Pix", "Pix"), ("SEPA", "SEPA"), ("ACH", "ACH"), ("UPI", "UPI"), ("SWIFT", "SWIFT"), ("Card", "Card")], max_length=32)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="wallet", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Escrow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(max_length=3)),
                ("state", models.CharField(choices=[("pending", "Pending funding"), ("locked", "Locked"), ("released", "Released"), ("refunded", "Refunded")], db_index=True, default="pending", max_length=16)),
                ("provider", models.CharField(blank=True, choices=[("stripe", "Stripe Connect"), ("dlocal", "dLocal")], max_length=16)),
                ("provider_ref", models.CharField(blank=True, db_index=True, max_length=128)),
                ("employer_signed_off", models.BooleanField(default=False)),
                ("talent_signed_off", models.BooleanField(default=False)),
                ("funded_at", models.DateTimeField(blank=True, null=True)),
                ("released_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("employer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="employer_escrows", to=settings.AUTH_USER_MODEL)),
                ("listing", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="escrow", to="jobs.listing")),
                ("talent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="talent_escrows", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name_plural": "escrows",
            },
        ),
        migrations.CreateModel(
            name="WalletTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tx_type", models.CharField(choices=[("credit", "Credit"), ("debit", "Debit"), ("escrow_lock", "Escrow lock"), ("escrow_release", "Escrow release"), ("escrow_refund", "Escrow refund"), ("payout", "Payout")], db_index=True, max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(max_length=3)),
                ("balance_after", models.DecimalField(decimal_places=2, max_digits=14)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("escrow", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="transactions", to="payments.escrow")),
                ("wallet", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="payments.wallet")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="wallet",
            constraint=models.CheckConstraint(condition=models.Q(("balance__gte", 0)), name="wallet_balance_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="escrow",
            constraint=models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="escrow_amount_positive"),
        ),
        migrations.AddConstraint(
            model_name="wallettransaction",
            constraint=models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="wallet_tx_amount_positive"),
        ),
    ]
