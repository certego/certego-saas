# Generated by Django 3.2.9 on 2022-02-15 11:19

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
            name="UserFeedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "appname",
                    models.CharField(
                        choices=[
                            ("ACCOUNTS", "Accounts"),
                            ("DRAGONFLY", "Dragonfly"),
                            ("INTELOWL", "Intelowl"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("BUG_REPORT", "BUG_REPORT"),
                            ("FEATURE_REQUEST", "FEATURE_REQUEST"),
                            ("OTHER", "OTHER"),
                        ],
                        max_length=32,
                    ),
                ),
                ("message", models.TextField()),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedbacks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "User Feedbacks",
            },
        ),
    ]