from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.permissions import BasePermission


class CacheTtl(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'cache_ttl'

class NeedToLogin(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'need_to_login'

class NeedToAnonymous(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'need_to_anonymous'



# class KycPermission(BasePermission):

#     def has_permission(self, request, view):
#         if not StartDarikex.objects.filter(start=True).exists():
#             raise NeedToStartDarikes
#         if not bool(request.user and request.user.is_authenticated):
#             raise NeedToLogin
#         elif not request.user.is_kyc:
#             raise NeedToKyc
#         else:
#             return True
