from django.contrib import admin

from .models import (
    Budget,
    Expense,
    ExpenseCategory,
    Income,
    IncomeCategory,
)


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):

    list_display = (
        "income_number",
        "category",
        "amount",
        "payment_method",
        "transaction_date",
        "reference",
        "recorded_by",
    )

    list_filter = (
        "payment_method",
        "category",
        "transaction_date",
    )

    search_fields = (
        "income_number",
        "reference",
        "description",
        "category__name",
    )

    readonly_fields = (
        "income_number",
        "created_at",
        "updated_at",
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    list_display = (
        "expense_number",
        "category",
        "amount",
        "payment_method",
        "transaction_date",
        "payee",
        "reference",
        "recorded_by",
    )

    list_filter = (
        "payment_method",
        "category",
        "transaction_date",
    )

    search_fields = (
        "expense_number",
        "reference",
        "description",
        "payee",
        "category__name",
    )

    readonly_fields = (
        "expense_number",
        "created_at",
        "updated_at",
    )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "financial_year",
        "category",
        "amount",
        "is_active",
        "created_by",
    )

    list_filter = (
        "financial_year",
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "category__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )