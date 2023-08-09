from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("certego_saas_notifications", "0002_alter_notification_appname"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="for_user",
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                related_name="notifications",
                help_text="If the field is empty, the notification is for everyone; otherwise only for the specified user",
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
    ]
