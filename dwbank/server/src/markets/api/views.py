import logging

from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from decimal import Decimal as D

from users.api.permissions import TokenPermission
from users.models import UserModel, Notification
from users.utils import otp_generate
from markets.api.serializer import LoanSerializer, CreateDepositSerializer, ChargeFiatSerializer,\
                                   SupportSerializer, CreditCardSerializer, TransferSerializer,\
                                   ListCreateDepositSerializer, ListCreditCardSerializer,\
                                   RequestCreateDepositSerializer, RequestCreditCardSerializer,\
                                   RequestLoanSerializer, RequestNotificationSerializer, GetBalanceSerializer,\
                                   TWithdrawalSerializer, TDepositSerializer, TInternalWithdrawalferSerializer, TInternalDepositferSerializer
from markets.functions import TronClient, PayPalClient, get_usd_balance, get_usdt_balance, get_euro_balance
from markets.models import FiatDepositHistory, InternalTransfers, Wallets, Withdrawal, Balances, CreditCard,\
                           CreateDeposit, CreditCard, Loan, DepositHistory, BlockFee, Wage
from markets.choices import StatusChoices, StateChoices
from markets.messages import Messages
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db import transaction
from django.core.cache import cache


logger = logging.getLogger(__name__)


class LoanViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = LoanSerializer
    permission_classes = (IsAuthenticated, TokenPermission)



class LoanNotifViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        user = self.request.user
        code = otp_generate()
        cache.set(f'loan_code_of_{user}', code, 60)
        user.send_credential_to_user(password=code, title='DWBANK LOAN', template_name='loan')
        return Response(Messages.SENT_CODE.value, status=status.HTTP_200_OK)


class BalanceNotifViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        user = self.request.user
        code = otp_generate()
        cache.set(f'balance_code_of_{user}', code, 60)
        user.send_credential_to_user(password=code, title='DWBANK BALANCE', template_name='balance')
        return Response(Messages.SENT_CODE.value, status=status.HTTP_200_OK)




class CreateDepositViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CreateDeposit.objects.all()
    permission_classes = (IsAuthenticated, TokenPermission)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateDepositSerializer
        elif self.action == 'list':
            return ListCreateDepositSerializer
    


class TetherDepositViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        tron_client = TronClient()
        deposit_address, network = tron_client.generate_address(user_id=user.id)
        return Response({'address': deposit_address, 'network': network}, status=status.HTTP_200_OK)


class chargeFiatViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=ChargeFiatSerializer ,responses={200: "https://www.sandbox.paypal.com/checkoutnow?token=8DM068874C338710X"})
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = ChargeFiatSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        obj = FiatDepositHistory.objects.create(user=user, **serializer.data)
        paypal_client = PayPalClient()
        link = paypal_client.generate_link(fiat_deposit_obj=obj)
        return Response({'link':link}, status=status.HTTP_200_OK)


class SupportViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SupportSerializer
    permission_classes = (IsAuthenticated,)


class CreditCardViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CreditCard.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreditCardSerializer
        elif self.action == 'list':
            return ListCreditCardSerializer


class BalanceViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get_balance(user):
        balances = {}
        balances['USDT'] = get_usdt_balance(user=user)
        balances['USD'] = 0#get_usd_balance(user=user)
        balances['EURO'] = 0#get_euro_balance(user=user)
        return balances
    
    @swagger_auto_schema(request_body=GetBalanceSerializer ,responses={200: ""})
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = GetBalanceSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        balance = BalanceViewSet.get_balance(user=user)
        return Response(balance, status=status.HTTP_200_OK)


class DshboardBalanceViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get_balance(user):
        balances = {}
        balances['USDT'] = get_usdt_balance(user=user)
        balances['USD'] = 0 #get_usd_balance(user=user)
        balances['EURO'] = 0 #get_euro_balance(user=user)
        return balances
 
    def list(self, request, *args, **kwargs):
        user = self.request.user
        balance = DshboardBalanceViewSet.get_balance(user=user)
        return Response(balance, status=status.HTTP_200_OK)
    
    

# class TransferViewSet(viewsets.ViewSet):
#     permission_classes = (IsAuthenticated,)

#     @swagger_auto_schema(request_body=TransferSerializer ,responses={200: ""})
#     def create(self, request, *args, **kwargs):
#         user = self.request.user
#         data = request.data
#         serializer = TransferSerializer(data=data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serialized_data = serializer.data
#         amount = serialized_data['amount']
#         destination_account_owner=serialized_data['destination_account_owner'],
#         behalf=serialized_data['behalf'],
#         description=serialized_data['description']
#         try:
#             match serialized_data['currency']:
#                 case 'USDT':
#                     tron_client = TronClient()
#                     wallet = get_object_or_404(Wallets, user=user)
#                     private_key = wallet.private_key
#                     from_address = wallet.address
#                     if serialized_data.get('destination_account_id'):
#                         to_wallet = get_object_or_404(Wallets, user__id=serialized_data['destination_wallet_id'])
#                         to_address = to_wallet.address
#                     else:
#                         to_address = serialized_data['destination_wallet_id']
#                     payload = tron_client.transfer_tether(from_address=from_address, to_address=to_address, private_key=private_key, amount=D(amount))
#                     # transfer wage
#                     if payload.get('receipt'):
#                         result = payload['receipt'].get('result')
#                         if result:
#                             if result == 'FAILED':
#                                 status_transfer = StatusChoices.FAILED
#                                 withdrawal_obj = Withdrawal.objects.create(
#                                     user=user,
#                                     address=to_address,
#                                     currency=serialized_data['currency'],
#                                     amount=amount,
#                                     destination_account_owner=destination_account_owner,
#                                     behalf=behalf,
#                                     description=description,
#                                     tx_id=payload['id'],
#                                     status = status_transfer
#                                 )
#                             elif result == 'SUCCESS':
#                                 status_transfer = StatusChoices.COMPLETED
#                                 wage = Wage.objects.last()
#                                 transfer_wage = wage.transfer_wage
#                                 block_amount = D(amount) * (transfer_wage / D('100'))
#                                 with transaction.atomic():
#                                     withdrawal_obj = Withdrawal.objects.create(
#                                         user=user,
#                                         address=to_address,
#                                         currency=serialized_data['currency'],
#                                         amount=amount,
#                                         destination_account_owner=destination_account_owner,
#                                         behalf=behalf,
#                                         description=description,
#                                         tx_id=payload['id'],
#                                         status = status_transfer
#                                     )    
#                                     BlockFee.objects.create(
#                                         user=user,
#                                         reason=withdrawal_obj,
#                                         currency='USDT',
#                                         amount=block_amount,
#                                         status=StatusChoices.TO_ACT
#                                     )
#                             else:
#                                 wage = Wage.objects.last()
#                                 transfer_wage = wage.transfer_wage
#                                 block_amount = D(amount) * (transfer_wage / D('100'))
#                                 with transaction.atomic():
#                                     withdrawal_obj = Withdrawal.objects.create(
#                                         user=user,
#                                         address=to_address,
#                                         currency=serialized_data['currency'],
#                                         amount=amount,
#                                         destination_account_owner=destination_account_owner,
#                                         behalf=behalf,
#                                         description=description,
#                                         tx_id=payload['id'],
#                                     )    
#                                     BlockFee.objects.create(
#                                         user=user,
#                                         reason=withdrawal_obj,
#                                         currency='USDT',
#                                         amount=block_amount
#                                     )
#                         tx_id = payload['id']
#                 case _:
#                     if serialized_data['destination_account_id']:
#                         to_user = get_object_or_404(UserModel, user__id=serialized_data['destination_account_id'])
#                         internal_transfer = InternalTransfers.objects.create(
#                             from_user=user,
#                             to_user=to_user,
#                             currency=serialized_data['currency'],
#                             amount=amount,
#                             destination_account_owner=destination_account_owner,
#                             behalf=behalf,
#                             description=description
#                         )
#                         tx_id = internal_transfer.id
                        
#                     else:
#                         paypal_client = PayPalClient()
#                         paypal_client.transfer()
#                         tx_id = 0
#         except Exception as e:
#             print(e)
#             raise ValidationError(e)
#         return Response("Your request is created", status=status.HTTP_200_OK)


class TransferViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=TransferSerializer ,responses={200: ""})
    def create(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        serializer = TransferSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data
        amount = serialized_data['amount']
        destination_account_owner=serialized_data['destination_account_owner'],
        behalf=serialized_data['behalf'],
        description=serialized_data['description']
        try:
            match serialized_data['currency']:
                case 'USDT':
                    if serialized_data.get('destination_account_id'):
                        to_wallet = get_object_or_404(Wallets, user__id=serialized_data['destination_wallet_id'])
                        to_address = to_wallet.address
                    else:
                        to_address = serialized_data['destination_wallet_id']
                        status_transfer = StatusChoices.PENDING
                        wage = Wage.objects.last()
                        transfer_wage = wage.transfer_wage
                        block_amount = D(amount) * (transfer_wage / D('100'))
                        with transaction.atomic():
                            withdrawal_obj = Withdrawal.objects.create(
                                user=user,
                                address=to_address,
                                currency=serialized_data['currency'],
                                amount=amount,
                                destination_account_owner=destination_account_owner,
                                behalf=behalf,
                                description=description,
                                status = status_transfer
                            )    
                            BlockFee.objects.create(
                                user=user,
                                reason=withdrawal_obj,
                                currency='USDT',
                                amount=block_amount,
                                status=StatusChoices.TO_ACT
                            )
                case _:
                    ...
        except Exception as e:
            raise ValidationError(e)
        return Response("Your request is created", status=status.HTTP_200_OK)
    

class TransactionViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        w = Wallets.objects.get(user=user)
        address = w.address
        t = TronClient()
        t.transaction_history(address=address)
        deposits = DepositHistory.objects.filter(to_address=address)
        print(deposits)
        deposit_transfers = InternalTransfers.objects.filter(to_user=user)
        Withdrawal_transfers = InternalTransfers.objects.filter(from_user=user)
        withdrawls = Withdrawal.objects.filter(user=user)
        deposits_data = TDepositSerializer(deposits, many=True).data
        deposit_transfers_data = TInternalDepositferSerializer(deposit_transfers, many=True).data
        Withdrawal_transfers_data = TInternalWithdrawalferSerializer(Withdrawal_transfers, many=True).data
        withdrawls_data = TWithdrawalSerializer(withdrawls, many=True).data

        details = []
        for i in deposits_data:
            details.append(i)
        for i in deposit_transfers_data:
            details.append(i)
        for i in Withdrawal_transfers_data:
            details.append(i)
        for i in withdrawls_data:
            details.append(i)
        return Response(details, status=status.HTTP_200_OK)



# class FiatDepositViewSet(viewsets):
#     permission_classes = (IsAuthenticated,)

#     def list(self, request, *args, **kwargs):
#         user = self.request.user
#         tron_client = TronClient()
#         deposit_address = tron_client.generate_address(user_id=user.id)
#         return Response({'detail': deposit_address}, status=status.HTTP_200_OK)

    
    # @swagger_auto_schema(request_body=WithDrawalEmaillSerializer ,responses={200: f"{UserMessages.SEND_CODE.value}"})
    # @action(detail=False, methods=['post'],permission_classes=(KycPermission, SendEmailWithDrawalPermission) ,url_path="send/email/(?P<coin>\w{1,10})")
    # def send_email(self, request, *args, **kwargs):
    #     coin = self.kwargs['coin']
    #     coin_serializer = CoinSerializers(data=self.kwargs)
    #     coin_serializer.is_valid(raise_exception=True)
    #     serializer = WithDrawalEmaillSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = request.user
    #     title = settings.WITHDRAWAL_TITLE
    #     ttl_time=settings.WITHDRAWAL_EMAIL_EXPIRED_TIME
    #     address, amount = serializer.data["address"], serializer.data["amount"]
    #     user.send_withdrawal_email_to_user(
    #         title=title, template_name="withdrawal",ttl_time=ttl_time, coin=coin,
    #         address=address, amount=amount
    #     )
    #     return Response({'detail': UserMessages.SEND_CODE.value}, status=status.HTTP_200_OK)



class UserRequestViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        user = self.request.user
        deposits = CreateDeposit.objects.filter(user=user)
        credit_cards = CreditCard.objects.filter(user=user)
        loans = Loan.objects.filter(user=user)
        notifs = Notification.objects.filter(user=user)
        deposits_data = RequestCreateDepositSerializer(deposits, many=True).data
        credit_cards_data = RequestCreditCardSerializer(credit_cards, many=True).data
        loans_data = RequestLoanSerializer(loans, many=True).data
        notifs_data = RequestNotificationSerializer(notifs ,many=True).data
        details = []
        for i in deposits_data:
            details.append(i)
        for i in credit_cards_data:
            details.append(i)
        for i in loans_data:
            details.append(i)
        for i in notifs_data:
            details.append(i)
        return Response(details, status=status.HTTP_200_OK)
