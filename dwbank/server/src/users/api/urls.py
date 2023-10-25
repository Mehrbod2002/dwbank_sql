from rest_framework.routers import DefaultRouter
from users.api.views import RegisterViewSet, LoginViewSet, NotificationViewSet, SignViewSet,\
                            ProfileViewSet, ChangePasswordViewSet, LogOut

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename="register")
router.register(r'login', LoginViewSet, basename="login")
router.register(r'notif/to/user', NotificationViewSet, basename="notification")
router.register(r'sign', SignViewSet, basename="sign")
router.register(r'profile', ProfileViewSet, basename="profile")
router.register(r'change/password', ChangePasswordViewSet, basename="change_password")
router.register(r'logout', LogOut, basename='logout')
