from enum import Enum
from django.utils.translation import gettext_lazy as _


class Messages(Enum):
    RESET_PASSWORD = _(".لینک بازیابی رمز عبور برای شما ارسال شد")
    MOBILE_OR_EMAIL = _("you must enter a mobile number or email")
    DUPLICATE_MOBILE_NUMBER = _("the mobile number is being used by another user")
    INCORRECT_CODE = _(".کد وارد شده اشتباه می باشد")
    EDIT_INFORMATION = _('user information is incorrect')
    NOT_FOUND_USER = _('user not found')
    INACTIVE_USER = _('user is not active')
    INCORRECT_PASSWORD_OR_ID = _('The password or account id is incorrect')
    INCORRECT_PHONE_NUMBER = _("mobile number is incorrect")
    TTL_ERROR = _('{} ثانیه دیگر تلاش کنید ')
    DUPLICATE_EMAIL = _("email is being used by another user")
    LOGIN_ERROR = _('you are logged in')
    LOGOUT = _(".شما با موفقیت از سایت خارج شدید")
    INVALID_RESET_LINK = _("the reset link is invalid")
    SET_NEW_PASSWORD = _("Password reset successfully") 
    REGISTER_SUCCESSFULL = _(".ثبت نام با موقیت انجام شد")
    EMAIL_NOT_EXISTS = _(".ایمیل وجود ندارد")
    NOT_ACTIVE_2FA = _(".تایید دو مرحله ای فعال نیست")
    ACTIVE_2FA = _(".تایید دو مرحله ای فعال شد")
    REPEAT_NEW_PASSWORD = _(".رمزهای عبور یکسان نیستند")
    FAIL_IN_REGISTER = _(".در روند ثبت نام مشکلی پیش آمده است")
    INVALID_FORMAT = _("The image format is incorrect")
    LOGIN_RESPONSE = """{
        "detail": {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjkzNTg3NTI4LCJpYXQiOjE2OTM1ODcyMjgsImp0aSI6IjA2ZmJmMmU1NmUyYzRjNzBhM2Y3ZTc3N2YzYzg1ZDcyIiwidXNlcl9pZCI6IjIxNDcyNDY1LWU1MDctNDYyNC05ZjY5LTAyMTI1ZGM1NjZiYiJ9.j5dGYLUWli43NrQ3HwgSX3_r7vA4IltBMPqY8Y7SIY8",
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5MzY3MzYyOCwiaWF0IjoxNjkzNTg3MjI4LCJqdGkiOiJkMzFmZjIyZjlmODg0ODdkOTk2YzkzMGQ4MjdkZjQ5NSIsInVzZXJfaWQiOiIyMTQ3MjQ2NS1lNTA3LTQ2MjQtOWY2OS0wMjEyNWRjNTY2YmIifQ.vH5RuCbHSu4KAiW3lVa4sxJ0iQqaz2qIdsMfoBjMbq4"
        }
    }"""
    SENT_CODE = _("The code has been sent to you")