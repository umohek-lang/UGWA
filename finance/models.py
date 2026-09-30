from django.conf import settings
from django.db import models


class IncomeCategory(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class Income(models.Model):

    class PaymentMethod(models.TextChoices):

        CASH = "CASH", "Cash"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        POS = "POS", "POS"
        ONLINE = "ONLINE", "Online"
        CHEQUE = "CHEQUE", "Cheque"
        OTHER = "OTHER", "Other"

    income_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    category = models.ForeignKey(
        IncomeCategory,
        on_delete=models.PROTECT,
        related_name="income_records"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    description = models.TextField(
        blank=True
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )

    transaction_date = models.DateField()

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recorded_income"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        creating = self.pk is None

        super().save(*args, **kwargs)

        if creating and not self.income_number:

            self.income_number = (
                f"INC-{self.pk:06d}"
            )

            super().save(
                update_fields=[
                    "income_number"
                ]
            )

    def __str__(self):

        return (
            self.income_number
            or f"Income #{self.pk}"
        )


class Expense(models.Model):

    class PaymentMethod(models.TextChoices):

        CASH = "CASH", "Cash"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        POS = "POS", "POS"
        CHEQUE = "CHEQUE", "Cheque"
        OTHER = "OTHER", "Other"

    expense_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expense_records"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    description = models.TextField()

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER
    )

    transaction_date = models.DateField()

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    payee = models.CharField(
        max_length=200,
        blank=True
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recorded_expenses"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        creating = self.pk is None

        super().save(*args, **kwargs)

        if creating and not self.expense_number:

            self.expense_number = (
                f"EXP-{self.pk:06d}"
            )

            super().save(
                update_fields=[
                    "expense_number"
                ]
            )

    def __str__(self):

        return (
            self.expense_number
            or f"Expense #{self.pk}"
        )


class Budget(models.Model):

    name = models.CharField(
        max_length=200
    )

    financial_year = models.PositiveIntegerField()

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="budgets"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_budgets"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-financial_year",
            "category__name",
        ]

    def __str__(self):

        return (
            f"{self.name} - "
            f"{self.financial_year}"
        )