from django.conf import settings
from django.db import models


class WelfareCase(models.Model):

    class CaseType(models.TextChoices):

        MEDICAL = "MEDICAL", "Medical Assistance"

        BEREAVEMENT = (
            "BEREAVEMENT",
            "Bereavement Assistance"
        )

        EMERGENCY = (
            "EMERGENCY",
            "Emergency Assistance"
        )

        EDUCATION = (
            "EDUCATION",
            "Education Support"
        )

        FAMILY = (
            "FAMILY",
            "Family Support"
        )

        FINANCIAL = (
            "FINANCIAL",
            "Financial Assistance"
        )

        OTHER = (
            "OTHER",
            "Other Welfare Support"
        )


    class Status(models.TextChoices):

        PENDING = (
            "PENDING",
            "Pending Review"
        )

        UNDER_REVIEW = (
            "UNDER_REVIEW",
            "Under Review"
        )

        MORE_INFO = (
            "MORE_INFO",
            "More Information Required"
        )

        APPROVED = (
            "APPROVED",
            "Approved"
        )

        PARTIALLY_APPROVED = (
            "PARTIALLY_APPROVED",
            "Partially Approved"
        )

        REJECTED = (
            "REJECTED",
            "Rejected"
        )

        PAID = (
            "PAID",
            "Paid"
        )

        CLOSED = (
            "CLOSED",
            "Closed"
        )


    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="welfare_cases"
    )

    case_type = models.CharField(
        max_length=30,
        choices=CaseType.choices
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    amount_requested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    amount_approved = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING
    )

    officer_remarks = models.TextField(
        blank=True
    )

    member_remarks = models.TextField(
        blank=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_welfare_cases"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "-created_at"
        ]


    def __str__(self):

        return (
            f"{self.title} - "
            f"{self.member.username}"
        )


class WelfarePayment(models.Model):

    case = models.ForeignKey(
        WelfareCase,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_date = models.DateField()

    payment_reference = models.CharField(
        max_length=100,
        blank=True
    )

    class PaymentMethod(models.TextChoices):

        CASH = "CASH", "Cash"

        BANK_TRANSFER = (
        "BANK_TRANSFER",
        "Bank Transfer"
    )

    POS = "POS", "POS"

    CHEQUE = "CHEQUE", "Cheque"

    OTHER = "OTHER", "Other"


    payment_method = models.CharField(
    max_length=30,
    choices=PaymentMethod.choices,
    blank=True
)

    notes = models.TextField(
        blank=True
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_welfare_payments"
    )

    finance_expense = models.OneToOneField(
         "finance.Expense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="welfare_payment"
)
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.case.title} - "
            f"{self.amount}"
        )
    class Meta:

        ordering = [
            "-payment_date",
            "-created_at"
        ]


