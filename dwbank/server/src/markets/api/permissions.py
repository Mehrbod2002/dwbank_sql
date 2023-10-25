from rest_framework.permissions import BasePermission
from reusable.permissions import NeedToAnonymous
from rest_framework.exceptions import PermissionDenied

class NotAuthenticatedPermission(BasePermission):

    def has_permission(self,request,view):
        if bool(request.auth):
            raise NeedToAnonymous
        return True
    

class TokenPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.sign_set.all():
            return True
        raise PermissionDenied('You must receive a token')
    

class TetherTransferPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.sign_set.all():
            return True
        raise PermissionDenied('You must receive a token')
    

class CryptoTransferPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.sign_set.all():
            return True
        raise PermissionDenied('You must receive a token')
