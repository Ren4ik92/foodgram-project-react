from django.contrib import admin
from .models import MyUser


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('user_type', 'username', 'first_name', 'last_name', 'email', 'password')


admin.site.register(MyUser, MyUserAdmin)
