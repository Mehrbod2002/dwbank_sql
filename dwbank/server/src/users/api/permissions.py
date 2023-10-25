from rest_framework.permissions import BasePermission, IsAuthenticated
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


class ProfilePermission(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        print(view.action)
        if view.action == 'partial_update':
            if obj.id == request.user.id:
                return True
        return False
