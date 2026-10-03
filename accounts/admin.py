from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'role', 'suburb', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'suburb')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'skills')
    fieldsets = UserAdmin.fieldsets + (
        ('LocalLink profile', {'fields': ('role', 'phone', 'suburb', 'postcode',
                                          'bio', 'skills', 'is_verified')}),
    )
