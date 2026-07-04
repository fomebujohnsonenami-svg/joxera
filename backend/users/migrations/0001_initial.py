from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
import pgvector.django


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0002_enable_pgvector"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("handle", models.CharField(db_index=True, max_length=30, unique=True)),
                ("role", models.CharField(choices=[("talent", "Talent"), ("employer", "Employer")], db_index=True, max_length=16)),
                ("country_code", models.CharField(db_index=True, max_length=2)),
                ("tier", models.CharField(choices=[("basic", "Basic"), ("verified", "Verified"), ("pro", "Pro")], default="basic", max_length=16)),
                ("kyc_status", models.CharField(choices=[("unverified", "Unverified"), ("pending", "Pending"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")], db_index=True, default="unverified", max_length=16)),
                ("verified_badge", models.BooleanField(default=False, help_text="Displayed when identity verification is complete.")),
                ("skill_tags", models.JSONField(blank=True, default=list, help_text="Normalized English skill tags extracted from profile/resume.")),
                ("skill_embedding", pgvector.django.VectorField(blank=True, dimensions=settings.SKILL_EMBEDDING_DIMENSIONS, help_text="Semantic embedding of normalized skills.", null=True)),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={
                "ordering": ["handle"],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddIndex(
            model_name="user",
            index=pgvector.django.HnswIndex(fields=["skill_embedding"], name="user_skill_emb_hnsw", opclasses=["vector_cosine_ops"]),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(condition=models.Q(("kyc_status", "approved"), _negated=True) | models.Q(("verified_badge", False)), name="verified_badge_requires_approved_kyc"),
        ),
        migrations.CreateModel(
            name="Entity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kyb_status", models.CharField(choices=[("unverified", "Unverified"), ("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], db_index=True, default="unverified", max_length=16)),
                ("business_type", models.CharField(choices=[("sole_prop", "Sole Proprietorship"), ("llc", "LLC"), ("corporation", "Corporation"), ("nonprofit", "Non-profit"), ("cooperative", "Cooperative")], max_length=32)),
                ("registration_no", models.CharField(blank=True, max_length=64)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="entity", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name_plural": "entities",
            },
        ),
        migrations.AddConstraint(
            model_name="entity",
            constraint=models.CheckConstraint(condition=models.Q(("kyb_status", "approved"), _negated=True) | models.Q(("registration_no", ""), _negated=True), name="approved_kyb_requires_registration_no"),
        ),
    ]
