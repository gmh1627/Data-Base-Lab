# Generated by Django 3.0.3 on 2020-06-12 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myWEB', '0010_remove_smtable_cs'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='yytable',
            unique_together={('dzid', 'isbn', 'yysj')},
        ),
    ]