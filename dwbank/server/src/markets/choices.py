from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CurrencyChoices(TextChoices):
    USDT = _('USDT')
    USD = _('USD')
    EURO = _('EURO')


class FiatChoices(TextChoices):
    USD = _('USD')
    EURO = _('EURO')


class StateChoices(TextChoices):
    Success = _('Success')
    Not_Accepted = _('Not_Accepted')
    Under_Review = _('Under_Review')


class DepositStateChoices(TextChoices):
    current = _('current')
    completed = _('completed')
    failed = _('failed')


class FiatDepositChoices(TextChoices):
    CREATED = _('CREATED')
    APPROVED = _('APPROVED')
    VOIDED = _('VOIDED')
    COMPLETED = _('COMPLETED')
    PAYER_ACTION_REQUIRED = _('PAYER_ACTION_REQUIRED')


class SubjectChoices(TextChoices):
    Card = _('Card')
    Wallet = _('Wallet')
    Transactions = _('Transactions')
    Requests = _('Requests')
    Digital_Sign = _('Digital_Sign')
    Transfer = _('Transfer')
    Deposit = _('Deposit')
    Profile = _('Profile')
    Last_Price = _('Last_Price')



class CardTypeChoices(TextChoices):
    Business_Card = _('Business_Card')
    Virtual_Card = _('Virtual_Card')


class CardLevelChoices(TextChoices):
    Gold = _('Gold')
    Silver = _('Silver')
    Normal = _("Normal")


class StatusChoices(TextChoices):
    COMPLETED = _('COMPLETED')
    TO_ACT = _('TO_ACT')
    PENDING = _('PENDING')
    FAILED = _('FAILED')
