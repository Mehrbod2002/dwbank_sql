import uuid
from users.messages import Messages
from users.models import UserModel, Notification, Sign
from markets.functions import TronClient
from markets.tasks import create_wallet

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import password_validation


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = (
            "id", "first_name", "nick_name", "last_name", "birthday", "id_number",
            "id_card_image", "passport_number", "passport_image", "phone_number", "email", "address"
        )
        extra_kwargs = {'first_name': {'required': True}, 'last_name': {'required':True}}
        read_only_fields = ('id',)

    def create(self, validated_data):
        tron_client = TronClient()
        password = validated_data.pop('password')
        obj = self.Meta.model.objects.create(**validated_data)
        obj.set_password(raw_password=password)
        obj.save()
        obj.send_credential_to_user(password=password, title='DWBANK PASSWORD', template_name='password')
        create_wallet.apply_async(args=(obj.id,))
        return obj


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = (
            "id", "first_name", "nick_name", "last_name", "birthday", "id_number",
            "id_card_image", "passport_number", "passport_image", "phone_number", "email", "address"
        )



class EditProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ("phone_number", "address")

    


class LoginSerializer(serializers.Serializer):
    account_id = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        id, password = attrs['account_id'], attrs['password']
        user = get_object_or_404(UserModel, pk=id)
        validated_password = user.check_password(password)
        if not validated_password:
            raise ValidationError(Messages.INCORRECT_PASSWORD_OR_ID.value)
        return attrs
    

class NotificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = Notification
        fields = ('deposit', 'deposit_and_withdraw', 'token')

    def validate_token(self, value):
        user = self.context.get('request').user
        try:
            get_object_or_404(Sign, user=user, token=value)
        except:
            raise ValidationError('the token is not valid')
        return value

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation.pop('token')
        return representation

    def create(self, validated_data):
        validated_data.pop('token')
        user = self.context.get('request').user
        validated_data['user'] = user
        if  self.Meta.model.objects.filter(user=user).count() == 0:
            obj = super().create(validated_data)
        else:
            instance = self.Meta.model.objects.filter(user=user).last()
            obj = self.update(instance=instance, validated_data=validated_data)
        return obj


class SignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sign
        fields = ('token',)
        read_only_fields = ('token',)

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['token'] = uuid.uuid4().hex
        validated_data['user'] = user
        if  self.Meta.model.objects.filter(user=user).count() == 0:
            obj = super().create(validated_data)
        else:
            instance = self.Meta.model.objects.filter(user=user).last()
            obj = self.update(instance=instance, validated_data=validated_data)
        return obj


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    repeat_new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise ValidationError(
                detail= Messages.INCORRECT_PASSWORD.value,
                code=f"translated_{ValidationError.default_code}"
            )
        return value
    
    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_repeat_new_password(self, value):
        new_password = self.initial_data['new_password']
        if not new_password == value:
            raise ValidationError(
                detail= Messages.DISMATCH_PASSWORD.value,
                code=f"translated_{ValidationError.default_code}"
            )
        return value


class LogOutSerializer(serializers.Serializer):
    token = serializers.CharField(allow_null=False, allow_blank=False)
