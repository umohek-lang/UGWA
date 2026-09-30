from django.contrib import admin

from .models import Executive


@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):

    list_display = (
        "position",
        "full_name",
        "display_order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "position",
        "full_name",
        "email",
    )

    ordering = (
        "display_order",
        "position",
    )