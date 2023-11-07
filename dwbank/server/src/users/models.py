import logging
import uuid
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.utils.timezone import now
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

from users.tasks import send_email
from users.utils import otp_generate, passport_image_path, id_card_image_path
from users.messages import Messages
from markets.choices import StateChoices
from markets.models import DepositHistory
from reusable.basemodels import BaseModel

logger = logging.getLogger(__name__)

class UserProfileManager(BaseUserManager):

    def create_user(self, email, password=None):
        """ Create a new user profile """
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """ Create a new superuser profile """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class UserModel(AbstractUser):
    id = models.UUIDField(_("Account_id"), default=uuid.uuid4, primary_key=True, unique=True)
    username = models.CharField(_("username"), max_length=150, null=True, blank=True)
    nick_name = models.CharField(_("Nick_name"), max_length=150, null=True, blank=True)
    phone_number = models.CharField(_("phone_number"), max_length=11, unique=True)
    email_is_verified = models.BooleanField(_("email_is_verified"), default=False)
    email = models.EmailField(_("email"), max_length=254, unique=True)
    phone_is_verified = models.BooleanField(_("Phone_is_verified"), default=False)
    id_number = models.CharField(_("Id_number"), max_length=150)
    id_card_image = models.ImageField(
        _("Id_card_image"), upload_to=id_card_image_path,
        max_length=1000, validators=[FileExtensionValidator(allowed_extensions=settings.SUPPORTED_IMAGE_FORMATS)])
    passport_number = models.CharField(_("Passport_number"), max_length=150)
    passport_image = models.ImageField(
        _("Passport_image"), upload_to=passport_image_path,
        max_length=1000, validators=[FileExtensionValidator(allowed_extensions=settings.SUPPORTED_IMAGE_FORMATS)])
    address = models.TextField(_("Address"))
    updated_at = models.DateTimeField(_("Updated_At"), auto_now=True)
    created_at = models.DateTimeField(_("Created_At"), auto_now_add=True)
    birthday = models.DateField(_('Birthday'), default=datetime.date(1992, 10, 10))

    USERNAME_FIELD = 'email'
    objects = UserProfileManager()
    REQUIRED_FIELDS = []


    def __str__(self) -> str:
        return f'{self.email}'

    def tokens(self):
        # refresh = RefreshToken.for_user(self)
        # return {
        #     "access": str(refresh.access_token),
        #     "refresh": str(refresh)
        # }
        token,_ = Token.objects.get_or_create(user=self)
        return {'token':token.key}
    
    def login(self, *args, **kwargs):
        # self.send_credential_to_user()
        return self.tokens(), status.HTTP_200_OK

    def logout(self, refresh):
        Token.objects.get(user=self).delete()
        return status.HTTP_200_OK, Messages.LOGOUT.value
    
    def send_credential_to_user(self, title, template_name, password):
        destination_email = self.email
        context = {"password":password, 'first_name':self.first_name, "last_name":self.last_name, 'account_id': self.id}
        print(context)
        # send_email.apply_async(args=(title, [destination_email], template_name, context))
        send_email.delay(title, [destination_email], template_name, context)

    def send_deposit_to_user(self, title, template_name , value, from_address, deposit_id):
        destination_email = self.email
        context = {"value":value, 'from_address':from_address,'first_name':self.first_name, "last_name":self.last_name, 'account_id': self.id}
        print(context)
        # send_email.apply_async(args=(title, [destination_email], template_name, context))
        send_email.delay(title, [destination_email], template_name, context)
        DepositHistory.objects.filter(id=deposit_id).update(email_is_sent=True)

    
    def send_withdrawal_to_user(self, title, template_name , value, to_address, status, currency):
        destination_email = self.email

        context = {
            "value":value, 'to_address':to_address,'first_name':self.first_name,
            "last_name":self.last_name, 'account_id': self.id,
            "status":status, "currency":currency
        }
        print(context)
        # send_email.apply_async(args=(title, [destination_email], template_name, context))
        if Notification.objects.filter(user=self).exists():
            notif = Notification.objects.filter(user=self).last()
            if notif.deposit_and_withdraw:
                send_email.delay(title, [destination_email], template_name, context)

    def change_password(self, new_password):
        self.set_password(new_password)
        self.save()
        return Messages.CHANGE_PASSWORD.value, status.HTTP_201_CREATED


class Notification(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    sms = models.BooleanField(_("Sms"), default=False)
    email = models.BooleanField(_("Email"), default=True)
    deposit = models.BooleanField(_("Deposit"), default=True)
    deposit_and_withdraw = models.BooleanField(_("Deposit_and_withdraw"), default=False)
    state = models.CharField(_("State"), max_length=50, choices=StateChoices.choices, default=StateChoices.Under_Review)

    def token(self):
        return
    
    def __str__(self):
        if self.deposit_and_withdraw:
            return "sms activation for deposit and withdrawal"
        else:
            return "sms activation for deposit"
    


class Sign(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), on_delete=models.CASCADE)
    token = models.CharField(_("Token"), max_length=250, unique=True)

    def __str__(self):
        return self.token
