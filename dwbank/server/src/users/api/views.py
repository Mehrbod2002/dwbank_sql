import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string

from users.api.serializer import RegisterSerializer, LoginSerializer, NotificationSerializer, SignSerializer,\
                                 ProfileSerializer, EditProfileSerializer, ChangePasswordSerializer, LogOutSerializer
from users.models import UserModel
from users.api.permissions import NotAuthenticatedPermission, TokenPermission, ProfilePermission
from users.messages import Messages

logger = logging.getLogger(__name__)

class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = RegisterSerializer
    permission_classes = (NotAuthenticatedPermission,)

    def perform_create(self, serializer):
        serializer.validated_data['password'] = get_random_string(length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*')
        return super().perform_create(serializer)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = (NotAuthenticatedPermission,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(request_body=LoginSerializer,
                         responses={200: openapi.Response(Messages.LOGIN_RESPONSE.value)})
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserModel.objects.get(pk=serializer.data['account_id'])
        detail, status = user.login()
        logger.info('the tokens return to user')
        return Response({'detail':detail}, status=status)
    

class NotificationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, TokenPermission)


class SignViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SignSerializer
    permission_classes = (IsAuthenticated,)


class ProfileViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = UserModel.objects.all()
    permission_classes = (ProfilePermission,)
    http_method_names = ('get', 'patch')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(pk=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfileSerializer
        elif self.action == 'partial_update':
            return EditProfileSerializer


class ChangePasswordViewSet(viewsets.ViewSet):
    """
    Using this class, the user can change his password
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    
    @swagger_auto_schema(request_body=ChangePasswordSerializer,
                         responses={201: openapi.Response(Messages.CHANGE_PASSWORD.value)})
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        new_password = data['new_password']
        detail, status = user.change_password(new_password)
        logger.info(f'the password of user_id {user.pk} is changed')
        return Response({'detail': detail}, status=status)
    

class LogOut(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogOutSerializer

    
    @swagger_auto_schema(request_body=LogOutSerializer, responses={200: ''})
    def create(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.data['token']
        user = request.user
        status, detail = user.logout(token)
        return Response({'detail': detail}, status=status)
