from django.db import migrations

# Dropping the old column is split out so it can be applied on a later deploy,
# once no instance is running code that still reads is_nda_member.


class Migration(migrations.Migration):

    dependencies = [
        ("moderate", "0024_backfill_is_employee"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mozillianprofile",
            name="is_nda_member",
        ),
    ]
