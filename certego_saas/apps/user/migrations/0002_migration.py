from django.db import OperationalError, migrations
from django.db.migrations.operations.base import Operation


class AlterCertegoSaasUser(Operation):
    reversible = True

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        vendor = schema_editor.connection.vendor

        for old, new in zip(
            [
                "certego_saas_user",
                "certego_saas_user_groups",
                "certego_saas_user_user_permissions",
            ],
            [
                "certego_saas_user_user",
                "certego_saas_user_user_groups",
                "certego_saas_user_user_user_permissions",
            ],
        ):
            try:
                schema_editor.execute(
                    f"ALTER TABLE {'IF EXISTS' if vendor == 'postgresql' else ''} {old} RENAME TO {new};"
                )
            except OperationalError:
                pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        vendor = schema_editor.connection.vendor
        for old, new in zip(
            [
                "certego_saas_user",
                "certego_saas_user_groups",
                "certego_saas_user_user_permissions",
            ],
            [
                "certego_saas_user_user",
                "certego_saas_user_user_groups",
                "certego_saas_user_user_user_permissions",
            ],
        ):
            try:
                schema_editor.execute(
                    f"ALTER TABLE {'IF EXISTS' if vendor == 'postgresql' else ''} {new} RENAME TO {old};"
                )
            except OperationalError:
                pass

    def describe(self):
        return "Alter Certego_saas_user table if necessary"


class Migration(migrations.Migration):
    dependencies = [
        ("certego_saas_user", "0001_initial"),
    ]

    operations = [AlterCertegoSaasUser()]
