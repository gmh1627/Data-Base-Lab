# Generated by Django 5.0.5 on 2024-07-04 04:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myWEB", "0025_alter_smtable_cbny"),
    ]

    operations = [
        migrations.AlterField(
            model_name="smtable",
            name="cbny",
            field=models.DateTimeField(),
        ),
    ]
