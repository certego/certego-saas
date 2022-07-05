from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("certego_saas_user", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS certego_saas_user RENAME TO certego_saas_user_user",
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS certego_saas_user_groups RENAME TO certego_saas_user_user_groups",
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS certego_saas_user_user_permissions RENAME TO certego_saas_user_user_user_permissions",
        ),
    ]
