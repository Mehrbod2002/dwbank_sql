import logging

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from reusable.basemodels import BaseModel
from markets.choices import CurrencyChoices, StateChoices, FiatChoices, FiatDepositChoices, SubjectChoices,\
                            CardTypeChoices, CardLevelChoices, StatusChoices, DepositStateChoices
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework.exceptions import PermissionDenied


logger = logging.getLogger(__name__)


class IntermediateWallet(BaseModel):
    private_key = models.CharField(_("private_key"), max_length=500, unique=True)
    address = models.CharField(_("address"), max_length=500,unique=True)

    def __str__(self):
        return 'this wallet address is used for network fee and activate addresses'

    def save(self, *args, **kwargs):
        if IntermediateWallet.objects.exclude(pk=self.pk).exists():
            raise PermissionDenied('A acount object already exists')
        return super().save(*args, **kwargs)
    
class Wallets(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(_("address"), max_length=500,unique=True)
    network = models.CharField(_("Network"), max_length=500, default="TRC20")
    tx_id_activation = models.CharField(_("tx_id_activation"), max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return self.address
    

class DepositHistory(BaseModel):
    to_address = models.CharField( max_length=500)
    value = models.CharField(max_length=500)
    tx_id = models.CharField(max_length=500, unique=True)
    time = models.CharField(max_length=500)
    email_is_sent = models.BooleanField(default=False)
    from_address = models.CharField(max_length=500)
    state = models.CharField(_("State"), max_length=50, choices=StateChoices.choices, default=StateChoices.Success)

    def __str__(self):
        return f"deposit to {self.to_address}%"
    
    def save(self, *args, **kwargs):
        wallet = Wallets.objects.get(address=self.to_address)
        user = wallet.user
        if not self.email_is_sent:
            user.send_deposit_to_user(title="DEPOSIT", template_name= 'deposit', value=self.value, from_address=self.from_address, deposit_id=self.id)
        return super().save(*args, **kwargs)


class CreateDeposit(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    currency = models.CharField(_("currency"), max_length=10, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2)
    deposit_time = models.IntegerField(_("Deposit_time"))
    interest = models.FloatField(_("Interest"))
    state = models.CharField(_("State"), max_length=50, choices=DepositStateChoices.choices, default=DepositStateChoices.current)

    def token(self):
        return

    def __str__(self) -> str:
        return f"deposit with {self.interest}% interest "


class FiatDepositHistory(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    currency = models.CharField(_("Currency"), max_length=10, choices=FiatChoices.choices)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2)
    deposit_id = models.CharField(_("Deposit_id"), max_length=200, blank=True, null=True)
    status = models.CharField(_("Status"), max_length=200, choices=FiatDepositChoices.choices, blank=True, null=True)

    def __str__(self) -> str:
        return self.currency


class InternalTransfers(BaseModel):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE, related_name='internal_witdrawal')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE, related_name='internal_deposit')
    currency = models.CharField(_("Currency"), max_length=10, choices=FiatChoices.choices)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2)
    destination_account_owner = models.CharField(_("destination_account_owner"), max_length=200)
    behalf = models.CharField(_("Behalf"), max_length=10)
    description = models.TextField(_("Description"))
    wage = models.DecimalField(_("Transfer_wage"), max_digits=5, decimal_places=2, default=3)

    def __str__(self):
        return f"destination account owner: {self.to_user} | behalf: {self.from_user} | {self.description} | wage: {self.wage}%"

    def save(self, *args, **kwargs):
        wage = Wage.objects.last()
        transfer_wage = wage.transfer_wage
        self.wage = transfer_wage
        return super().save(*args, **kwargs)
        
   
class Balances(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    currency = models.CharField(_("currency"), max_length=10, choices=CurrencyChoices.choices)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return self.currency
    

class Withdrawal(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    currency = models.CharField(_("currency"), max_length=10, choices=CurrencyChoices.choices)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2)
    tx_id = models.CharField(_("Tx_id"), max_length=500, blank=True, null=True)
    status = models.CharField(_("Status"), max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    address = models.CharField(_("address"), max_length=200)
    destination_account_owner = models.CharField(_("destination_account_owner"), max_length=200)
    behalf = models.CharField(_("Behalf"), max_length=100)
    description = models.TextField(_("Description"))
    wage = models.DecimalField(_("Transfer_wage"), max_digits=5, decimal_places=2, default=3)

    def __str__(self):
        return f"destination account owner: {self.user} | behalf: {self.address} | {self.description} | wage: {self.wage}%"

    def save(self, *args, **kwargs):
        user = self.user
        if self.status == StatusChoices.COMPLETED:
            user.send_withdrawal_to_user(
                title="WITHDRAWAL", template_name= 'withdraw', value=self.amount,
                to_address=self.address, status=self.status, currency=self.currency
            )
        wage = Wage.objects.last()
        transfer_wage = wage.transfer_wage
        self.wage = transfer_wage
        return super().save(*args, **kwargs)


class Loan(BaseModel):
    currency = models.CharField(_("currency"), max_length=10, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    loan_amount = models.DecimalField(_("Loan_amount"), max_digits=20, decimal_places=8)
    payment_time = models.IntegerField(_("Payment_time"))
    installment = models.DecimalField(_("Installment"), max_digits=20, decimal_places=8, default=0)
    state = models.CharField(_("State"), max_length=50, choices=StateChoices.choices, default=StateChoices.Under_Review)

    def code(self):
        return

    def __str__(self):
        wage = Wage.objects.last()
        loan_wage = wage.loan_wage
        return f"wage: {loan_wage}% | installment: {self.installment}{self.currency} per month "
    
    def token(self):
        return
    

class Wage(BaseModel):
    loan_wage = models.DecimalField(_("Loan_wage"), max_digits=5, decimal_places=2, default=3)
    transfer_wage = models.DecimalField(_("Transfer_wage"), max_digits=5, decimal_places=2, default=3)

    def __str__(self):
        return f"{self.loan_wage}  {self.transfer_wage}"


class Support(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    subject = models.CharField(_("Subject"), max_length=20, choices=SubjectChoices.choices)
    title = models.CharField(_("Title"), max_length=100)
    message = models.TextField(_("Message"))
    state = models.CharField(_("State"), max_length=50, choices=StateChoices.choices, default=StateChoices.Under_Review)

    def __str__(self):
        return self.title


class CreditCard(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    card_type = models.CharField(_("Card_type"), max_length=20, choices=CardTypeChoices.choices)
    card_level = models.CharField(_("Card_level"), max_length=20, choices=CardLevelChoices.choices)
    currency = models.CharField(_("currency"), max_length=10, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2)
    state = models.CharField(_("State"), max_length=50, choices=StateChoices.choices, default=StateChoices.Under_Review)

    def __str__(self):
        return f"card type: {self.card_type} | card level: {self.card_level} | charge amount: {self.amount} {self.currency}"
    
    def token(self):
        return
    


class EmailLoan(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    code = code = models.CharField(_("Code"), max_length=20)

    def __str__(self):
        return self.code


class EmailBalance(EmailLoan):
    ...


class BlockFee(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    currency = models.CharField(_("currency"), max_length=10, choices=CurrencyChoices.choices)
    tx_id = models.CharField(_("Tx_id"), max_length=500, null=True, blank=True)
    amount = models.DecimalField(_("Amount"), max_digits=20, decimal_places=2)
    status = models.CharField(_("Status"), max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    reason_content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Reason_content_type"),
        on_delete=models.CASCADE
    )
    reason_object_id = models.CharField(_("Reason_object_id"), max_length=50)
    reason = GenericForeignKey('reason_content_type', 'reason_object_id')
  
    def __str__(self):
        return f"block {self.amount} {self.currency} from {self.user}"


class FeeLimit(BaseModel):
    fee_limtt = models.IntegerField(_("Fee_limit"), editable=False)

    def __str__(self):
        return f'{self.fee_limtt}'
    

