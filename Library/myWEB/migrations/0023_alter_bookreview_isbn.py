# Generated by Django 5.0.5 on 2024-06-28 07:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myWEB", "0022_remove_bookreview_created_at_bookreview_comment_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookreview",
            name="isbn",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="myWEB.smtable"
            ),
        ),
    ]
