from django.contrib import admin

from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "event_type",
        "venue",
        "start_date",
        "registration_required",
        "is_published",
    )

    list_filter = (
        "event_type",
        "registration_required",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
        "venue",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "event",
        "member",
        "status",
        "registered_at",
        "attended_at",
    )

    list_filter = (
        "status",
        "event",
    )

    search_fields = (
        "event__title",
        "member__username",
        "member__first_name",
        "member__last_name",
        "member__email",
    )

    readonly_fields = (
        "registered_at",
    )