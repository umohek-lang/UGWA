from django.contrib import admin

from .models import DuesType, Invoice, Payment


@admin.register(DuesType)
class DuesTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "amount",
        "frequency",
        "is_active",
        "created_at",
    )

    list_filter = (
        "frequency",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "member",
        "dues_type",
        "amount",
        "amount_paid",
        "get_balance",
        "status",
        "due_date",
    )

    list_filter = (
        "status",
        "dues_type",
    )

    search_fields = (
        "invoice_number",
        "member__username",
        "member__first_name",
        "member__last_name",
        "member__email",
    )

    readonly_fields = (
        "invoice_number",
        "created_at",
        "updated_at",
    )

    def get_balance(self, obj):

        return obj.balance

    get_balance.short_description = "Balance"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "receipt_number",
        "payment_reference",
        "member",
        "invoice",
        "amount",
        "payment_method",
        "channel",
        "status",
        "paid_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "channel",
    )

    search_fields = (
        "receipt_number",
        "payment_reference",
        "member__username",
        "member__first_name",
        "member__last_name",
        "member__email",
    )

    readonly_fields = (
        "receipt_number",
        "gateway_transaction_id",
        "gateway_response",
        "channel",
        "created_at",
    )