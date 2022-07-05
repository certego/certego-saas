from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("certego_saas_user", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE IF EXISTS certego_saas_user RENAME TO certego_saas_user_user;"
            ],
            reverse_sql=[
                "ALTER TABLE IF EXISTS certego_saas_user_user RENAME TO certego_saas_user;"
            ],
        ),
        migrations.RunSQL(
            sql=[
                "ALTER TABLE IF EXISTS certego_saas_user_groups RENAME TO certego_saas_user_user_groups;"
            ],
            reverse_sql=[
                "ALTER TABLE IF EXISTS certego_saas_user_user_groups RENAME TO certego_saas_user_groups;"
            ],
        ),
        migrations.RunSQL(
            sql=[
                "ALTER TABLE IF EXISTS certego_saas_user_user_permissions RENAME TO certego_saas_user_user_user_permissions;"
            ],
            reverse_sql=[
                "ALTER TABLE IF EXISTS certego_saas_user_user_user_permissions RENAME TO certego_saas_user_user_permissions;"
            ],
        ),
    ]
