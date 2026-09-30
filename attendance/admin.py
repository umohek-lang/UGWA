from django.contrib import admin

from .models import (
    AttendanceRecord,
    AttendanceSession,
)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "session_type",
        "date",
        "start_time",
        "venue",
        "is_open",
        "created_by",
    )

    list_filter = (
        "session_type",
        "date",
        "is_open",
    )

    search_fields = (
        "title",
        "description",
        "venue",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):

    list_display = (
        "session",
        "member",
        "status",
        "check_in",
        "check_out",
        "marked_by",
        "created_at",
    )

    list_filter = (
        "status",
        "session",
    )

    search_fields = (
        "member__username",
        "member__first_name",
        "member__last_name",
        "session__title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "member",
        "marked_by",
        "session",
    )