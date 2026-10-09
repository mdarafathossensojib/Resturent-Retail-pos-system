
from django.db import migrations, models


def set_existing_superuser_roles(apps, schema_editor):
    User = apps.get_model("users", "User")
    db = schema_editor.connection.alias

    User.objects.using(db).filter(
        is_superuser=True
    ).update(role="admin")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("manager", "Manager"),
                    ("cashier", "Cashier"),
                ],
                default="cashier",
                max_length=10,
            ),
        ),
        migrations.RunPython(
            set_existing_superuser_roles,
            migrations.RunPython.noop,
        ),
    ]