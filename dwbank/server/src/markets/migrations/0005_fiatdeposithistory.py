# Generated by Django 4.2.5 on 2023-09-12 04:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('markets', '0004_alter_createdeposit_interest'),
    ]

    operations = [
        migrations.CreateModel(
            name='FiatDepositHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated_At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created_At')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is_Deleted')),
                ('currency', models.CharField(choices=[('USD', 'Usd'), ('EURO', 'Euro')], max_length=10, verbose_name='Currency')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Amount')),
                ('deposit_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='Deposit_id')),
                ('status', models.CharField(blank=True, choices=[('CREATED', 'Created'), ('APPROVED', 'Approved'), ('VOIDED', 'Voided'), ('COMPLETED', 'Completed'), ('PAYER_ACTION_REQUIRED', 'Payer Action Required')], max_length=200, null=True, verbose_name='Status')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
