# Generated by Django 5.0.5 on 2024-06-11 12:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myWEB", "0017_rename_gh_tsglytable_glyid"),
    ]

    operations = [
        migrations.AddField(
            model_name="jstable",
            name="is_valid",
            field=models.BooleanField(default=True),
        ),
    ]
