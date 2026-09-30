from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_approved",
        "is_active",
        "membership_code",
        "membership_status",
        "membership_date",
    )

    list_filter = (
        "role",
        "is_approved",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "membership_code",
        "first_name",
        "last_name",
        "phone",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Association Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "is_approved",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Association Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "is_approved",
                )
            },
        ),
    )