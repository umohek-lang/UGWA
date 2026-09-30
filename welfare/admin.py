from django.contrib import admin

from .models import (
    WelfareCase,
    WelfarePayment,
)


@admin.register(WelfareCase)
class WelfareCaseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "member",
        "case_type",
        "amount_requested",
        "amount_approved",
        "status",
        "reviewed_by",
        "created_at",
    )

    list_filter = (
        "case_type",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "member__username",
        "member__first_name",
        "member__last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "reviewed_at",
        "paid_at",
    )

    autocomplete_fields = (
        "member",
        "reviewed_by",
    )


@admin.register(WelfarePayment)
class WelfarePaymentAdmin(admin.ModelAdmin):

    list_display = (
        "case",
        "amount",
        "payment_date",
        "payment_reference",
        "payment_method",
        "recorded_by",
    )

    list_filter = (
        "payment_date",
        "payment_method",
    )

    search_fields = (
        "case__title",
        "payment_reference",
        "case__member__username",
    )

    autocomplete_fields = (
        "case",
        "recorded_by",
    )