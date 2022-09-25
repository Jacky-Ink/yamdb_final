from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'bio',
        'role'
    )
    search_fields = ('username',)
    list_filter = ('role',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
