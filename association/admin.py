from django.contrib import admin

from .models import AssociationProfile


@admin.register(AssociationProfile)
class AssociationProfileAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "short_name",
        "email",
        "phone",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "short_name",
        "email",
        "phone",
    )