from django.contrib import admin
from .models import Notification, Sign, UserModel
from django.contrib.auth.admin import UserAdmin


admin.site.register(Notification)
admin.site.register(Sign)

@admin.register(UserModel)
class UserAdmin(UserAdmin):
      fieldsets = ((('User'),{'fields':('password',)}),
      (('personal_info'),{'fields':("id", 'first_name','last_name','email', 'phone_number', 'id_number','id_card_image','passport_number','passport_image', 'address', 'birthday')}),
      (('permissions'),{'fields':('is_active', 'phone_is_verified', 'is_staff', 'email_is_verified',
            'is_superuser','groups', 'user_permissions')}),
      (('Important dates'),{'fields':('last_login', 'date_joined')}))
      add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
      )
      list_display = ['email', 'phone_number']
      search_fields = ['email', 'phone_number']
      list_per_page =10



