import django.contrib.gis.db.models.fields
import django.db.models.deletion
import pgvector.django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Listing",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("field", models.CharField(db_index=True, help_text="Domain or trade field (e.g. plumbing, backend-dev).", max_length=64)),
                ("tier", models.CharField(choices=[("standard", "Standard"), ("priority", "Priority"), ("enterprise", "Enterprise")], default="standard", max_length=16)),
                ("mode", models.CharField(choices=[("remote", "Remote"), ("onsite", "On-site"), ("hybrid", "Hybrid")], db_index=True, max_length=16)),
                ("country_code", models.CharField(db_index=True, max_length=2)),
                ("geo_point", django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, help_text="WGS-84 point for on-site/hybrid jobs; null for fully remote.", null=True, srid=4326)),
                ("currency", models.CharField(max_length=3)),
                ("budget", models.DecimalField(decimal_places=2, max_digits=14)),
                ("escrow_id", models.CharField(blank=True, db_index=True, max_length=64)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("closed", "Closed"), ("filled", "Filled"), ("cancelled", "Cancelled")], db_index=True, default="draft", max_length=16)),
                ("skill_tags", models.JSONField(blank=True, default=list, help_text="LLM-normalized skill tags (English) extracted from description.")),
                ("skill_embedding", pgvector.django.VectorField(blank=True, dimensions=768, help_text="Semantic embedding of title + normalized skills.", null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="listings", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("reviewing", "Reviewing"), ("accepted", "Accepted"), ("rejected", "Rejected"), ("withdrawn", "Withdrawn")], db_index=True, default="pending", max_length=16)),
                ("cover_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("listing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="jobs.listing")),
                ("talent", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="listing",
            index=models.Index(fields=["country_code", "status"], name="listing_country_status_idx"),
        ),
        migrations.AddIndex(
            model_name="listing",
            index=pgvector.django.HnswIndex(fields=["skill_embedding"], name="listing_skill_emb_hnsw", opclasses=["vector_cosine_ops"]),
        ),
        migrations.AddConstraint(
            model_name="listing",
            constraint=models.CheckConstraint(condition=models.Q(("budget__gt", 0)), name="listing_budget_positive"),
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(fields=("listing", "talent"), name="unique_application_per_listing_talent"),
        ),
    ]
