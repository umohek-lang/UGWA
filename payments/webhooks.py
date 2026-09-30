import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from accounts.models import User
from .models import Invoice
from .services import (
    record_successful_paystack_payment,
    verify_paystack_transaction,
)


@csrf_exempt
def paystack_webhook(request):

    if request.method != "POST":

        return HttpResponse(
            status=405
        )

    signature = request.headers.get(
        "x-paystack-signature"
    )

    if not signature:

        return HttpResponse(
            status=401
        )

    payload = request.body

    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(
        expected_signature,
        signature,
    ):

        return HttpResponse(
            status=401
        )

    try:

        event = json.loads(
            payload.decode("utf-8")
        )

    except json.JSONDecodeError:

        return HttpResponse(
            status=400
        )

    event_name = event.get(
        "event"
    )

    if event_name != "charge.success":

        return HttpResponse(
            status=200
        )

    transaction_data = event.get(
        "data",
        {}
    )

    reference = transaction_data.get(
        "reference"
    )

    if not reference:

        return HttpResponse(
            status=400
        )

    # Confirm the transaction directly with Paystack.
    try:

        verification = verify_paystack_transaction(
            reference
        )

    except Exception:

        return HttpResponse(
            status=500
        )

    if not verification.get("status"):

        return HttpResponse(
            status=400
        )

    verified_data = verification.get(
        "data",
        {}
    )

    if verified_data.get("status") != "success":

        return HttpResponse(
            status=200
        )

    # We expect references such as:
    #
    # INV-000001-a83c91f4e3a8b7c2
    #
    parts = reference.split("-")

    if len(parts) < 3:

        return HttpResponse(
            status=400
        )

    invoice_number = (
        f"{parts[0]}-{parts[1]}"
    )

    invoice = Invoice.objects.filter(
        invoice_number=invoice_number
    ).first()

    if not invoice:

        return HttpResponse(
            status=404
        )

    member = invoice.member

    payment, created = (
        record_successful_paystack_payment(
            verified_data,
            member,
            invoice,
        )
    )

    return HttpResponse(
        status=200
    )