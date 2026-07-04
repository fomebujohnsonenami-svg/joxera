from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_country_config"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
    ]
