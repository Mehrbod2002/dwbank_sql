# Generated by Django 4.2.5 on 2023-09-15 22:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_usermodel_birthday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='birthday',
            field=models.DateField(default=datetime.datetime(2023, 9, 15, 22, 34, 33, 486670, tzinfo=datetime.timezone.utc), verbose_name='Birthday'),
        ),
    ]
