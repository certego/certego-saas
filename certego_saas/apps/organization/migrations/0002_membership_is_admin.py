from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("certego_saas_organization", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]
