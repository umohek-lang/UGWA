from django.contrib import admin

from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "city",
        "state",
        "phone",
        "is_active",
    )

    list_filter = (
        "is_active",
        "state",
    )

    search_fields = (
        "name",
        "code",
        "city",
        "state",
    )