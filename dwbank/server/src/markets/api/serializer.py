from decimal import Decimal as D

from users.models import Sign, Notification
from markets.models import Loan, Wage, CreateDeposit, Support, CreditCard, Wallets, InternalTransfers, Withdrawal,\
                           DepositHistory, BlockFee
from markets.choices import FiatChoices, CurrencyChoices, StatusChoices
from markets.functions import get_euro_balance, get_usd_balance, get_usdt_balance, TronClient

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.dateparse import parse_datetime
from django.core.cache import cache



class CreateDepositSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    token = serializers.CharField(write_only=True)

    class Meta:
        model = CreateDeposit
        fields = ('amount', 'deposit_time', 'interest', 'token', 'currency', 'user')

    def validate_amount(self, value):
        user = self.context.get('request').user

        match self.initial_data['currency']:
            case 'USDT':
                if value > get_usdt_balance(user):
                    raise ValidationError('Your Tether balance is not enough')
            case 'EURO':
                # TODO EDIT
                # if value > get_euro_balance(user):
                    raise ValidationError('Your euro balance is not enough')
            case 'USD':
                # if value > get_usd_balance(user):
                    raise ValidationError('Your usd balance is not enough')
        return value


    def validate_token(self, value):
        user = self.context.get('request').user
        try:
            get_object_or_404(Sign, user=user, token=value)
        except:
            raise ValidationError('the token is not valid')
        return value
    
    def validate_deposit_time(self, value):
        if not 2 < value < 61:
            raise ValidationError('The deposit time must be between 3 and 60 month')
        return value
              
    def create(self, validated_data):
        validated_data.pop('token')
        obj = super().create(validated_data)
        BlockFee.objects.create(
            user=validated_data['user'],
            amount=validated_data['amount'],
            currency=validated_data['currency'],
            reason=obj,
            status=StatusChoices.TO_ACT
        )
        return obj


class ListCreateDepositSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    start_date = serializers.CharField(source='created_at')

    class Meta:
        model = CreateDeposit
        fields = ('tracking_number', 'amount', 'deposit_time', 'interest', 'currency', 'state', 'start_date')

    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['start_date']
        start_date_obj = parse_datetime(start_date)
        representation['start_date'] = start_date_obj.date()
        representation['end_date'] = start_date_obj.date() + relativedelta(months = representation['deposit_time'])
        return representation



class LoanSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    token = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)

    class Meta:
        model = Loan
        fields = ('loan_amount', 'payment_time', 'installment', 'token', 'currency', 'user', 'code')
        read_only_fields = ('installment',)

    def validate_token(self, value):
        user = self.context.get('request').user
        try:
            get_object_or_404(Sign, user=user, token=value)
        except:
            raise ValidationError('the token is not valid')
        return value
    
    def validate_payment_time(self, value):
        if not 9 < value < 25:
            raise ValidationError('The payment time must be between 10 and 24')
        return value

    def validate_code(self, value):
        user = self.context.get('request').user
        cached_code = cache.get(f'loan_code_of_{user}')
        if not value == cached_code:
            raise ValidationError('The code is not correct')
        return value

    def create(self, validated_data):
        validated_data.pop('token')
        validated_data.pop('code')
        obj = super().create(validated_data)
        wage = Wage.objects.last().loan_wage
        payment_time = obj.payment_time
        loan_amount = obj.loan_amount
        installment = (((loan_amount * (wage /D('100')))) + loan_amount) / payment_time
        obj.installment = round(installment,2)
        obj.save()
        return obj



class ChargeFiatSerializer(serializers.Serializer):
    amount = serializers.CharField(max_length=12)
    currency = serializers.ChoiceField(choices=FiatChoices.choices)


class SupportSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Support
        fields = ('user', 'subject', 'title', 'message')


class CreditCardSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CreditCard
        fields = ('user', 'card_type', 'card_level', 'currency', 'amount', 'token')

    def validate_amount(self, value):
        user = self.context.get('request').user

        match self.initial_data['currency']:
            case 'USDT':
                if value > get_usdt_balance(user):
                    raise ValidationError('Your Tether balance is not enough')

            case 'EURO':
                # if value > get_euro_balance(user):
                    raise ValidationError('Your euro balance is not enough')
            case 'USD':
                # if value > get_usd_balance(user):
                    raise ValidationError('Your usd balance is not enough')
        return value


    def validate_token(self, value):
        user = self.context.get('request').user
        try:
            get_object_or_404(Sign, user=user, token=value)
        except:
            raise ValidationError('the token is not valid')
        return value

    def create(self, validated_data):
        validated_data.pop('token')
        obj = super().create(validated_data)
        return obj


class ListCreditCardSerializer(serializers.ModelSerializer):
    issue_tracking_number = serializers.CharField(source='id')
    issue_date = serializers.CharField(source='created_at')
    charge_amount = serializers.CharField(source='amount')

    class Meta:
        model = CreditCard
        fields = ('issue_tracking_number', 'issue_date', 'card_type', 'card_level', 'currency', 'charge_amount')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        issue_date = representation['issue_date']
        issue_date_obj = parse_datetime(issue_date)
        representation['issue_date'] = issue_date_obj.date()
        return representation

    

class TransferSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    currency = serializers.ChoiceField(choices=CurrencyChoices.choices)
    destination_account_id = serializers.CharField(max_length=100, required=False)
    destination_wallet_id = serializers.CharField(max_length=100, required=False)
    destination_account_owner =  serializers.CharField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    behalf = serializers.CharField(max_length=100)
    description = serializers.CharField()

    # def validate_destination_wallet_id(self, value):
    #     if value:
    #         tron_client = TronClient()
    #         if tron_client.is_address(value):
    #             return value
    #         else:
    #             raise ValidationError('the address is incorrect fro trc20')
    #     else:
    #         return value
    
    def validate_amount(self, value):
        user = self.context.get('request').user
        currency = self.initial_data['currency']
        wage = Wage.objects.last()
        transfer_wage = wage.transfer_wage
        match currency:
            case "USD":
                #TODO EDIT
                balance = 0#get_usd_balance(user=user)
            case "USDT":
                balance = get_usdt_balance(user=user)
            case "EURO":
                #TODO EDIT
                balance = 0#get_euro_balance(user=user)
        if (value + (value * (transfer_wage / D('100')))) >= D(str(balance)):
            raise ValidationError('Your balance is not enough')
        self.to_representation
        return value

    def validate_token(self, value):
        user = self.context.get('request').user
        try:
            get_object_or_404(Sign, user=user, token=value)
        except:
            raise ValidationError('the token is not valid')
        return value

    def validate_currency(self, value):
        if value in ['USD', 'EURO']:
            raise ValidationError('Euro and Dollar transfer will start soon')
        return value
    
    def validate(self, attrs):
        a = attrs.get('destination_account_id')
        b = attrs.get('destination_wallet_id')
        if (a or b) and not (a and b):
            return attrs
        else:
            raise ValidationError('One must choose between wallet and account')
            
            
class RequestCreateDepositSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    time = serializers.CharField(source='deposit_time')
    description = serializers.CharField(source='__str__')

    class Meta:
        model = CreateDeposit
        fields = ('tracking_number', 'amount', 'time', 'currency', 'state', 'date', 'description')

    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['request_name'] = 'Create A Deposit'
        return representation


class RequestCreditCardSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    description = serializers.CharField(source='__str__')

    class Meta:
        model = CreditCard
        fields = ('tracking_number', 'amount', 'currency', 'state', 'date', 'description')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['request_name'] = 'Request A Credit Card'
        return representation


class RequestNotificationSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    description = serializers.CharField(source='__str__')

    class Meta:
        model = CreditCard
        fields = ('tracking_number', 'state', 'date', 'description')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['request_name'] = 'SMS Activation'
        return representation


class RequestLoanSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    amount = serializers.CharField(source='loan_amount')
    time = serializers.CharField(source='payment_time')
    description = serializers.CharField(source='__str__')

    class Meta:
        model = Loan
        fields = ('tracking_number', 'amount', 'currency', 'time', 'state', 'date', 'description')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['request_name'] = 'Request A Loan'
        return representation



class GetBalanceSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    

    def validate_token(self, value):
        user = self.context.get('request').user
        try:
            get_object_or_404(Sign, user=user, token=value)
        except:
            raise ValidationError('the token is not valid')
        return value
    
    def validate_password(self, value):
        user = self.context.get('request').user
        validated_password = user.check_password(value)
        print(validated_password)
        if not validated_password:
            raise ValidationError('The password is incorrect')
        return value

    def validate_code(self, value):
        user = self.context.get('request').user
        cached_code = cache.get(f'balance_code_of_{user}')
        if not value == cached_code:
            raise ValidationError('The code is not correct')
        return value


class TDepositSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    description = serializers.CharField(source='__str__')
    origin = serializers.CharField(source='from_address')
    destination = serializers.CharField(source='to_address')
    amount = serializers.CharField(source='value')

    class Meta:
        model = DepositHistory
        fields = ('tracking_number', 'origin', 'date', 'description', 'destination', 'amount', 'state')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['amount'] = D(representation['amount']) / D('1000000')
        representation['type'] = 'Balance Increase'
        representation['currency'] = 'USDT'
        return representation


class TWithdrawalSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    description = serializers.CharField(source='__str__')
    state = serializers.CharField(source='status')
    origin = serializers.SerializerMethodField()
    destination = serializers.CharField(source='address')

    class Meta:
        model = Withdrawal
        fields = ('tracking_number', 'origin', 'date', 'description', 'destination', 'amount', 'state')

    def get_origin(self, obj):
        user= obj.user
        wallet = Wallets.objects.get(user=user)
        return wallet.address

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['type'] = 'Transfer'
        return representation
    

class TInternalDepositferSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    description = serializers.CharField(source='__str__')
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    class Meta:
        model = InternalTransfers

        fields = ('tracking_number', 'origin', 'date', 'description', 'destination', 'amount', 'state')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['type'] = 'Balance Increase'
        return representation
    
    def get_origin(self, obj):
        user = obj.from_user
        wallet = Wallets.objects.get(user=user)
        return wallet.address
    
    def get_destination(self, obj):
        user = obj.to_user
        wallet = Wallets.objects.get(user=user)
        return wallet.address
    


class TInternalWithdrawalferSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(source='id')
    date = serializers.CharField(source='created_at')
    description = serializers.CharField(source='__str__')
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    class Meta:
        model = InternalTransfers

        fields = ('tracking_number', 'origin', 'date', 'description', 'destination', 'amount', 'state')

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        start_date = representation['date']
        start_date_obj = parse_datetime(start_date)
        representation['date'] = start_date_obj.date()
        representation['type'] = 'Transfer'
        return representation
    
    def get_origin(self, obj):
        user = obj.from_user
        wallet = Wallets.objects.get(USER=user)
        return wallet.address
    
    def get_destination(self, obj):
        user = obj.to_user
        wallet = Wallets.objects.get(USER=user)
        return wallet.address
