from django.conf import settings
from django.db import models


class DuesType(models.Model):

    class Frequency(models.TextChoices):
        ANNUAL = "ANNUAL", "Annual"
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        ONE_TIME = "ONE_TIME", "One Time"

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.ANNUAL
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


class Invoice(models.Model):

    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIAL = "PARTIAL", "Partially Paid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices"
    )

    dues_type = models.ForeignKey(
        DuesType,
        on_delete=models.PROTECT,
        related_name="invoices"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    due_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID
    )

    description = models.TextField(
        blank=True
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

        if creating and not self.invoice_number:
            self.invoice_number = f"INV-{self.pk:06d}"

            super().save(
                update_fields=["invoice_number"]
            )

    def update_status(self):

        if self.amount_paid <= 0:
            self.status = self.Status.UNPAID

        elif self.amount_paid < self.amount:
            self.status = self.Status.PARTIAL

        else:
            self.status = self.Status.PAID

        self.save(
            update_fields=[
                "amount_paid",
                "status",
                "updated_at",
            ]
        )

    @property
    def balance(self):

        remaining = self.amount - self.amount_paid

        if remaining < 0:
            return 0

        return remaining

    def __str__(self):
        return self.invoice_number or f"Invoice #{self.pk}"


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Successful"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    payment_reference = models.CharField(
        max_length=100,
        unique=True
    )

    gateway_transaction_id = models.BigIntegerField(
        blank=True,
        null=True
    )

    gateway_response = models.CharField(
        max_length=255,
        blank=True
    )

    channel = models.CharField(
        max_length=50,
        blank=True
    )

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50,
        default="ONLINE"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        creating = self.pk is None

        super().save(*args, **kwargs)

        if creating and not self.receipt_number:

            self.receipt_number = (
                f"RCT-{self.pk:06d}"
            )

            super().save(
                update_fields=["receipt_number"]
            )

    def __str__(self):
        return self.payment_reference


class DuesSchedule(models.Model):

    class Frequency(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        HALF_YEARLY = "HALF_YEARLY", "Half Yearly"
        YEARLY = "YEARLY", "Yearly"
        ONE_TIME = "ONE_TIME", "One Time"

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dues_schedules",
    )

    dues_type = models.ForeignKey(
        DuesType,
        on_delete=models.PROTECT,
        related_name="schedules",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.MONTHLY,
    )

    start_date = models.DateField()

    next_due_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_dues_schedules",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-is_active",
            "next_due_date",
        ]

    def __str__(self):
        return (
            f"{self.member.username} - "
            f"{self.dues_type.name}"
        )

    