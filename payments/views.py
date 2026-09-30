import uuid
from django.db.models import Sum
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from .models import Invoice, Payment
from .services import (
    initialize_paystack_transaction,
    record_successful_paystack_payment,
    verify_paystack_transaction,
)
from .models import Invoice, Payment
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .decorators import membership_officer_required
from .forms import DuesTypeForm, DuesScheduleForm
from .models import DuesType, DuesSchedule
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .forms import MemberEditForm

@login_required
def payment_history(request):

    payments = Payment.objects.filter(
        member=request.user
    ).order_by("-created_at")

    return render(
        request,
        "payments/payment_history.html",
        {
            "payments": payments,
        }
    )


@login_required
def invoices(request):

    invoice_list = Invoice.objects.filter(
        member=request.user
    ).order_by("-created_at")

    total_outstanding = sum(
        invoice.balance
        for invoice in invoice_list
    )

    return render(
        request,
        "payments/invoices.html",
        {
            "invoices": invoice_list,
            "total_outstanding": total_outstanding,
        }
    )


@login_required
def invoice_detail(request, invoice_number):

    invoice = get_object_or_404(
        Invoice,
        invoice_number=invoice_number
    )

    payments = invoice.payments.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "payments/invoice_detail.html",
        {
            "invoice": invoice,
            "payments": payments,
        }
    )


@login_required
def pay_invoice(request, invoice_number):

    invoice = get_object_or_404(
        Invoice,
        invoice_number=invoice_number,
        member=request.user
    )

    if invoice.status == Invoice.Status.CANCELLED:

        messages.error(
            request,
            "This invoice has been cancelled."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    if invoice.balance <= 0:

        messages.info(
            request,
            "This invoice has already been fully paid."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    if not request.user.email:

        messages.error(
            request,
            "Please add an email address to your account before making payment."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    reference = (
        f"{invoice.invoice_number}-"
        f"{uuid.uuid4().hex[:16]}"
    )

    callback_url = request.build_absolute_uri(
        reverse("payments:paystack_callback")
    )

    try:

        response = initialize_paystack_transaction(
            email=request.user.email,
            amount=invoice.balance,
            reference=reference,
            callback_url=callback_url,
        )

    except Exception:

        messages.error(
            request,
            "Unable to initialize the payment. Please try again."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    if not response.get("status"):

        messages.error(
            request,
            "Paystack could not initialize this payment."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    authorization_url = response["data"]["authorization_url"]

    return redirect(
        authorization_url
    )


@login_required
def paystack_callback(request):

    reference = request.GET.get(
        "reference"
    )

    if not reference:

        messages.error(
            request,
            "Payment reference was not provided."
        )

        return redirect(
            "payments:invoices"
        )

    try:

        response = verify_paystack_transaction(
            reference
        )

    except Exception:

        messages.error(
            request,
            "Unable to verify the payment."
        )

        return redirect(
            "payments:invoices"
        )

    if not response.get("status"):

        messages.error(
            request,
            "Payment verification failed."
        )

        return redirect(
            "payments:invoices"
        )

    transaction = response.get(
        "data",
        {}
    )

    if transaction.get("status") != "success":

        messages.error(
            request,
            "The Paystack transaction was not successful."
        )

        return redirect(
            "payments:invoices"
        )

    invoice_number = reference.split(
        "-",
        2
    )[0] + "-" + reference.split(
        "-",
        2
    )[1]

    invoice = get_object_or_404(
        Invoice,
        invoice_number=invoice_number,
        member=request.user
    )

    expected_amount = int(
        invoice.balance * 100
    )

    paid_amount = int(
        transaction.get("amount", 0)
    )

    if paid_amount != expected_amount:

        messages.error(
            request,
            "The payment amount could not be verified."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    if transaction.get("currency") != "NGN":

        messages.error(
            request,
            "The payment currency could not be verified."
        )

        return redirect(
            "payments:invoice_detail",
            invoice_number=invoice.invoice_number
        )

    payment, created = record_successful_paystack_payment(
    transaction,
    request.user,
    invoice,
)

    if payment is None:

        messages.error(
        request,
        "The payment could not be recorded."
    )

    return redirect(
        "payments:invoice_detail",
        invoice_number=invoice.invoice_number
    )

    if not created:

        messages.info(
            request,
        "This payment has already been recorded."
    )

    else:

     messages.success(
            request,
        "Payment successful! Your invoice has been updated."
    )



@login_required
def payment_receipt(request, receipt_number):

    payment = get_object_or_404(
        Payment,
        receipt_number=receipt_number,
        member=request.user
    )

    return render(
        request,
        "payments/payment_receipt.html",
        {
            "payment": payment,
        }
    )


@login_required
def membership_dashboard(request):

    invoices = (
        Invoice.objects
        .filter(
            member=request.user
        )
        .exclude(
            status=Invoice.Status.CANCELLED
        )
        .annotate(
            calculated_balance=ExpressionWrapper(
                F("amount") - F("amount_paid"),
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2
                )
            )
        )
    )

    total_invoiced = (
        invoices.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0")
    )

    total_paid = (
        invoices.aggregate(
            total=Sum("amount_paid")
        ).get("total")
        or Decimal("0")
    )

    total_outstanding = (
        invoices.aggregate(
            total=Sum("calculated_balance")
        ).get("total")
        or Decimal("0")
    )

    outstanding_invoices = (
        invoices
        .filter(
            calculated_balance__gt=0
        )
        .order_by(
            "due_date"
        )
    )

    recent_payments = (
        Payment.objects
        .filter(
            member=request.user
        )
        .select_related(
            "invoice"
        )
        .order_by(
            "-paid_at",
            "-created_at"
        )[:10]
    )

    context = {
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
        "outstanding_invoices": outstanding_invoices,
        "recent_payments": recent_payments,
    }

    return render(
        request,
        "payments/membership_dashboard.html",
        context
    )


@login_required
def membership_card(request):

    return render(
        request,
        "payments/membership_card.html"
    )

@login_required
@membership_officer_required
def dues_type_list(request):

    dues_types = DuesType.objects.all().order_by(
        "-is_active",
        "name",
    )

    return render(
        request,
        "payments/dues_type_list.html",
        {
            "dues_types": dues_types,
        }
    )






@login_required
@membership_officer_required
def dues_type_create(request):

    if request.method == "POST":

        form = DuesTypeForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Dues type created successfully."
            )

            return redirect(
                "payments:dues_type_list"
            )

    else:

        form = DuesTypeForm()

    return render(
        request,
        "payments/dues_type_form.html",
        {
            "form": form,
            "page_title": "Create Dues Type",
        }
    )


@login_required
@membership_officer_required
def dues_schedule_list(request):

    schedules = (
        DuesSchedule.objects
        .select_related(
            "member",
            "dues_type",
            "created_by",
        )
        .order_by(
            "next_due_date"
        )
    )

    return render(
        request,
        "payments/dues_schedule_list.html",
        {
            "schedules": schedules,
        }
    )


@login_required
@membership_officer_required
def dues_schedule_create(request):

    if request.method == "POST":

        form = DuesScheduleForm(
            request.POST
        )

        if form.is_valid():

            schedule = form.save(
                commit=False
            )

            schedule.created_by = request.user

            schedule.save()

            messages.success(
                request,
                "Dues schedule created successfully."
            )

            return redirect(
                "payments:dues_schedule_list"
            )

    else:

        form = DuesScheduleForm()

    return render(
        request,
        "payments/dues_schedule_form.html",
        {
            "form": form,
            "page_title": "Create Dues Schedule",
        }
    )


@login_required
@membership_officer_required
def generate_invoice(request, schedule_id):

    schedule = get_object_or_404(
        DuesSchedule.objects.select_related(
            "member",
            "dues_type",
        ),
        pk=schedule_id,
        is_active=True,
    )

    invoice = Invoice.objects.create(
        member=schedule.member,
        dues_type=schedule.dues_type,
        amount=schedule.amount,
        due_date=schedule.next_due_date,
        description=(
            f"{schedule.dues_type.name} - "
            f"{schedule.next_due_date.strftime('%B %Y')}"
        ),
    )

    messages.success(
        request,
        (
            f"Invoice {invoice.invoice_number} "
            "has been generated successfully."
        )
    )

    return redirect(
        "payments:invoice_detail",
        invoice.invoice_number
    )



@login_required
def receipt_detail(request, receipt_number):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "member",
            "invoice",
        ),
        receipt_number=receipt_number,
        member=request.user,
        status=Payment.Status.SUCCESS,
    )

    return render(
        request,
        "payments/receipt_detail.html",
        {
            "payment": payment,
        }
    )

@login_required
@membership_officer_required
def membership_officer_dashboard(request):

    User = get_user_model()

    members = User.objects.filter(
        role=User.Role.MEMBER
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        members = members.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(membership_code__icontains=search)
        )

    total_members = User.objects.filter(
        role=User.Role.MEMBER
    ).count()

    active_members = User.objects.filter(
        role=User.Role.MEMBER,
        membership_status="ACTIVE",
    ).count()

    inactive_members = User.objects.filter(
        role=User.Role.MEMBER
    ).exclude(
        membership_status="ACTIVE"
    ).count()

    invoices = Invoice.objects.all()

    total_outstanding = (
        invoices.annotate(
    balance=F("amount") - F("amount_paid")
).filter(
    balance__gt=0
).aggregate(
            total=Sum("balance")
        ).get("total")
        or Decimal("0")
    )

    total_invoiced = (
        invoices.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0")
    )

    total_paid = (
        invoices.aggregate(
            total=Sum("amount_paid")
        ).get("total")
        or Decimal("0")
    )

    context = {
        "members": members.order_by(
            "first_name",
            "last_name",
        ),

        "search": search,

        "total_members": total_members,

        "active_members": active_members,

        "inactive_members": inactive_members,

        "total_outstanding": total_outstanding,

        "total_invoiced": total_invoiced,

        "total_paid": total_paid,
    }

    return render(
        request,
        "payments/membership_officer_dashboard.html",
        context
    )




@login_required
@membership_officer_required
def member_detail(request, member_id):

    User = get_user_model()

    member = get_object_or_404(
        User,
        pk=member_id,
        role=User.Role.MEMBER,
    )

    invoices = (
        Invoice.objects
        .filter(member=member)
        .exclude(status=Invoice.Status.CANCELLED)
        .order_by("-due_date")
    )

    payments = (
        Payment.objects
        .filter(member=member)
        .order_by("-paid_at", "-created_at")
    )

    total_invoiced = (
    invoices.aggregate(
        total=Sum("amount")
    ).get("total")
    or Decimal("0")
)

    total_paid = (
    invoices.aggregate(
        total=Sum("amount_paid")
    ).get("total")
    or Decimal("0")
)

    total_outstanding = sum(
    (invoice.balance for invoice in invoices),
    Decimal("0")
)

    context = {
        "member": member,
        "invoices": invoices,
        "payments": payments,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
    }

    return render(
        request,
        "payments/member_detail.html",
        context,
    )

@login_required
@membership_officer_required
def member_edit(request, member_id):

    User = get_user_model()

    member = get_object_or_404(
        User,
        pk=member_id,
        role=User.Role.MEMBER,
    )

    if request.method == "POST":

        form = MemberEditForm(
            request.POST,
            request.FILES,
            instance=member,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Member information updated successfully."
            )

            return redirect(
                "payments:member_detail",
                member_id=member.id,
            )

    else:

        form = MemberEditForm(
            instance=member
        )

    return render(
        request,
        "payments/member_edit.html",
        {
            "form": form,
            "member": member,
        }
    )


@login_required
def membership_card(request):

    member = request.user

    if not member.membership_code:

        messages.error(
            request,
            "Your membership code has not been assigned yet."
        )

        return redirect(
            "payments:membership_dashboard"
        )

    return render(
        request,
        "payments/membership_card.html",
        {
            "member": member,
        }
    )

def verify_membership(request, membership_code):

    User = get_user_model()

    member = get_object_or_404(
        User,
        membership_code=membership_code,
        role=User.Role.MEMBER,
    )

    return render(
        request,
        "payments/verify_membership.html",
        {
            "member": member,
        }
    )

@login_required
@membership_officer_required
def suspend_member(request, member_id):

    User = get_user_model()

    member = get_object_or_404(
        User,
        pk=member_id,
        role=User.Role.MEMBER,
    )

    if request.method == "POST":

        member.membership_status = User.MembershipStatus.SUSPENDED
        member.save(
            update_fields=["membership_status"]
        )

        messages.success(
            request,
            f"{member.get_full_name() or member.username} "
            "has been suspended successfully."
        )

    return redirect(
        "payments:member_detail",
        member_id=member.id,
    )


@login_required
@membership_officer_required
def reactivate_member(request, member_id):

    User = get_user_model()

    member = get_object_or_404(
        User,
        pk=member_id,
        role=User.Role.MEMBER,
    )

    if request.method == "POST":

        member.membership_status = User.MembershipStatus.ACTIVE
        member.save(
            update_fields=["membership_status"]
        )

        messages.success(
            request,
            f"{member.get_full_name() or member.username} "
            "has been reactivated successfully."
        )

    return redirect(
        "payments:member_detail",
        member_id=member.id,
    )