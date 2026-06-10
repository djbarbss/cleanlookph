from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {
            "fields": ("phone", "birthday"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Fields", {
            "fields": ("phone", "birthday"),
        }),
    )

    list_display = ("username", "email", "first_name", "last_name", "phone", "birthday", "is_staff")