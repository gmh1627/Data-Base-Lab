# Generated by Django 2.2.10 on 2021-08-25 17:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0025_auto_20210825_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowrecord',
            name='end_day',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 1, 17, 57, 38, 36825, tzinfo=utc)),
        ),
    ]
