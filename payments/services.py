import requests

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from finance.models import Income, IncomeCategory

from .models import Payment


def update_invoice_from_payments(invoice):
    """
    Recalculate an invoice using all successful payments
    attached to that invoice.
    """

    if not invoice:
        return

    total_paid = (
        Payment.objects
        .filter(
            invoice=invoice,
            status=Payment.Status.SUCCESS,
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or 0
    )

    if total_paid > invoice.amount:
        total_paid = invoice.amount

    invoice.amount_paid = total_paid
    invoice.update_status()


def initialize_paystack_transaction(
    email,
    amount,
    reference,
    callback_url,
):
    """
    Initialize a Paystack transaction.

    Amount is received in naira and converted to kobo
    before being sent to Paystack.
    """

    amount_in_kobo = int(amount * 100)

    url = (
        f"{settings.PAYSTACK_BASE_URL}"
        "/transaction/initialize"
    )

    headers = {
        "Authorization": (
            f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "email": email,
        "amount": str(amount_in_kobo),
        "currency": "NGN",
        "reference": reference,
        "callback_url": callback_url,
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def verify_paystack_transaction(reference):
    """
    Verify a Paystack transaction.
    """

    url = (
        f"{settings.PAYSTACK_BASE_URL}"
        f"/transaction/verify/{reference}"
    )

    headers = {
        "Authorization": (
            f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        ),
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


@transaction.atomic
def record_successful_paystack_payment(
    transaction_data,
    member,
    invoice,
):
    """
    Record a verified Paystack payment.

    This function can be reused by both
    the Paystack callback and webhook.
    """

    reference = transaction_data.get("reference")
    amount = transaction_data.get("amount")
    currency = transaction_data.get("currency")
    status = transaction_data.get("status")

    # Payment must be successful.
    if status != "success":
        return None, False

    # Only NGN payments are accepted.
    if currency != "NGN":
        return None, False

    # Reference is required.
    if not reference:
        return None, False

    # Amount is required.
    if not amount:
        return None, False

    # Convert Paystack kobo to naira.
    paid_amount = amount / 100

    # Prevent duplicate payment records.
    existing_payment = Payment.objects.filter(
        payment_reference=reference
    ).first()

    if existing_payment:
        return existing_payment, False

    # Payment must not exceed the outstanding invoice balance.
    if paid_amount > invoice.balance:
        return None, False

    # Create the payment record.
    payment = Payment.objects.create(
        payment_reference=reference,
        member=member,
        invoice=invoice,
        amount=paid_amount,
        payment_method="PAYSTACK",
        channel=transaction_data.get("channel", ""),
        gateway_transaction_id=transaction_data.get("id"),
        gateway_response=transaction_data.get(
            "gateway_response",
            "",
        ),
        status=Payment.Status.SUCCESS,
        paid_at=timezone.now(),
    )

    # ---------------------------------------------------------
    # FINANCE: MEMBERSHIP DUES INCOME
    # ---------------------------------------------------------

    membership_category, _ = IncomeCategory.objects.get_or_create(
        name="Membership Dues",
        defaults={
            "description": (
                "Income received from association "
                "membership dues and subscriptions."
            ),
            "is_active": True,
        },
    )

    # Prevent duplicate income entries.
    existing_income = Income.objects.filter(
        reference=payment.receipt_number
    ).first()

    if not existing_income:
        Income.objects.create(
            category=membership_category,
            amount=payment.amount,
            description=(
                "Membership dues payment from "
                f"{member.get_full_name() or member.username} "
                f"({member.membership_code}). "
                f"Invoice: {invoice.invoice_number}. "
                f"Receipt: {payment.receipt_number}."
            ),
            payment_method=payment.payment_method,
            transaction_date=payment.paid_at.date(),
            reference=payment.receipt_number,
            recorded_by=None,
        )

    return payment, True
