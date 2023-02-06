from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'password',
        'email',
        'is_staff',
        'is_active',
        'date_joined'
    )
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'
