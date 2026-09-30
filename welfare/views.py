from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from finance.models import Expense, ExpenseCategory

from .models import WelfareCase, WelfarePayment


# ================================================================
# WELFARE CASE LIST
# ================================================================

@login_required
def case_list(request):

    # Only staff/admin users can view all welfare cases.
    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):
        return redirect("welfare:my")

    cases = WelfareCase.objects.select_related(
        "member",
        "reviewed_by",
    ).order_by("-created_at")

    pending_count = cases.filter(
        status=WelfareCase.Status.PENDING
    ).count()

    approved_count = cases.filter(
        status=WelfareCase.Status.APPROVED
    ).count()

    paid_count = cases.filter(
        status=WelfareCase.Status.PAID
    ).count()

    context = {
        "cases": cases,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "paid_count": paid_count,
    }

    return render(
        request,
        "welfare/case_list.html",
        context,
    )


# ================================================================
# MEMBER'S WELFARE CASES
# ================================================================

@login_required
def my_cases(request):

    cases = WelfareCase.objects.filter(
        member=request.user
    ).order_by("-created_at")

    return render(
        request,
        "welfare/my_cases.html",
        {
            "cases": cases,
        },
    )


# ================================================================
# CREATE WELFARE CASE
# ================================================================

@login_required
def case_create(request):

    if request.method == "POST":

        case_type = request.POST.get(
            "case_type"
        )

        title = request.POST.get(
            "title"
        )

        description = request.POST.get(
            "description"
        )

        amount_requested = request.POST.get(
            "amount_requested",
            "0",
        )

        member_remarks = request.POST.get(
            "member_remarks",
            "",
        )

        # --------------------------------------------------------
        # Validate required fields
        # --------------------------------------------------------

        if not title or not description:

            messages.error(
                request,
                "Please complete all required fields.",
            )

            return render(
                request,
                "welfare/case_form.html",
            )

        # --------------------------------------------------------
        # Validate requested amount
        # --------------------------------------------------------

        try:

            amount_requested = Decimal(
                str(amount_requested or "0")
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):

            messages.error(
                request,
                "Please enter a valid requested amount.",
            )

            return render(
                request,
                "welfare/case_form.html",
            )

        if amount_requested <= Decimal("0"):

            messages.error(
                request,
                "Requested amount must be greater than zero.",
            )

            return render(
                request,
                "welfare/case_form.html",
            )

        # --------------------------------------------------------
        # Create welfare case
        # --------------------------------------------------------

        WelfareCase.objects.create(
            member=request.user,
            case_type=case_type,
            title=title,
            description=description,
            amount_requested=amount_requested,
            member_remarks=member_remarks,
        )

        messages.success(
            request,
            "Your welfare request has been submitted successfully.",
        )

        return redirect(
            "welfare:my"
        )

    return render(
        request,
        "welfare/case_form.html",
    )


# ================================================================
# WELFARE CASE DETAIL
# ================================================================

@login_required
def case_detail(request, pk):

    case = get_object_or_404(
        WelfareCase.objects.select_related(
            "member",
            "reviewed_by",
        ),
        pk=pk,
    )

    # ------------------------------------------------------------
    # Permission check
    # ------------------------------------------------------------

    if (
        case.member != request.user
        and not request.user.is_staff
        and not request.user.is_superuser
    ):

        messages.error(
            request,
            "You do not have permission to view this welfare case.",
        )

        return redirect(
            "welfare:my"
        )

    # ------------------------------------------------------------
    # Payments
    # ------------------------------------------------------------

    payments = case.payments.all().order_by(
        "-payment_date",
        "-id",
    )

    # ------------------------------------------------------------
    # Total paid
    # ------------------------------------------------------------

    total_paid = (
        payments.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0")
    )

    # ------------------------------------------------------------
    # Remaining approved amount
    # ------------------------------------------------------------

    remaining_amount = (
        case.amount_approved - total_paid
    )

    if remaining_amount < Decimal("0"):
        remaining_amount = Decimal("0")

    # ------------------------------------------------------------
    # Permission
    # ------------------------------------------------------------

    can_review = (
        request.user.is_staff
        or request.user.is_superuser
    )

    context = {
        "case": case,
        "payments": payments,
        "total_paid": total_paid,
        "remaining_amount": remaining_amount,
        "can_review": can_review,
        "status_choices": WelfareCase.Status.choices,
    }

    return render(
        request,
        "welfare/case_detail.html",
        context,
    )


# ================================================================
# REVIEW WELFARE CASE
# ================================================================

@login_required
def review_case(request, pk):

    # Only staff/admin users can review welfare cases.
    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        messages.error(
            request,
            "You do not have permission to review welfare cases.",
        )

        return redirect(
            "welfare:my"
        )

    case = get_object_or_404(
        WelfareCase,
        pk=pk,
    )

    # ------------------------------------------------------------
    # POST ONLY
    # ------------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # Get submitted values
    # ------------------------------------------------------------

    status = request.POST.get(
        "status"
    )

    amount_approved_raw = request.POST.get(
        "amount_approved",
        "0",
    )

    officer_remarks = request.POST.get(
        "officer_remarks",
        "",
    ).strip()

    # ------------------------------------------------------------
    # Validate status
    # ------------------------------------------------------------

    valid_statuses = [
        value
        for value, label in WelfareCase.Status.choices
    ]

    if status not in valid_statuses:

        messages.error(
            request,
            "Invalid welfare request status.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # Validate approved amount
    # ------------------------------------------------------------

    try:

        amount_approved = Decimal(
            str(amount_approved_raw or "0")
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        messages.error(
            request,
            "Invalid approved amount.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    if amount_approved < Decimal("0"):

        messages.error(
            request,
            "Approved amount cannot be negative.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # Approved amount cannot exceed requested amount
    # ------------------------------------------------------------

    if amount_approved > case.amount_requested:

        messages.error(
            request,
            "Approved amount cannot exceed the requested amount.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # Update case
    # ------------------------------------------------------------

    case.status = status

    case.amount_approved = amount_approved

    case.officer_remarks = officer_remarks

    case.reviewed_by = request.user

    case.reviewed_at = timezone.now()

    # ------------------------------------------------------------
    # PAID DATE
    # ------------------------------------------------------------

    if status == WelfareCase.Status.PAID:

        case.paid_at = timezone.now()

    else:

        case.paid_at = None

    case.save()

    messages.success(
        request,
        "Welfare request has been updated successfully.",
    )

    return redirect(
        "welfare:detail",
        pk=case.pk,
    )


# ================================================================
# RECORD WELFARE PAYMENT
# ================================================================

@login_required
def record_payment(request, pk):

    # ------------------------------------------------------------
    # AUTHORIZATION
    # ------------------------------------------------------------

    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        messages.error(
            request,
            "You do not have permission to record welfare payments.",
        )

        return redirect(
            "welfare:my"
        )

    # ------------------------------------------------------------
    # GET CASE
    # ------------------------------------------------------------

    case = get_object_or_404(
        WelfareCase,
        pk=pk,
    )

    # ------------------------------------------------------------
    # POST ONLY
    # ------------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # CHECK CASE STATUS
    # ------------------------------------------------------------

    if case.status not in [
        WelfareCase.Status.APPROVED,
        WelfareCase.Status.PARTIALLY_APPROVED,
    ]:

        messages.error(
            request,
            "This welfare request has not been approved for payment.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # GET FORM DATA
    # ------------------------------------------------------------

    amount_raw = request.POST.get(
        "amount",
        "",
    ).strip()

    payment_date = request.POST.get(
        "payment_date",
        "",
    ).strip()

    payment_method = request.POST.get(
        "payment_method",
        "",
    ).strip()

    payment_reference = request.POST.get(
        "payment_reference",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    # ============================================================
    # VALIDATE PAYMENT AMOUNT
    # ============================================================

    try:

        amount = Decimal(
            amount_raw
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        messages.error(
            request,
            "Please enter a valid payment amount.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    if amount <= Decimal("0"):

        messages.error(
            request,
            "Payment amount must be greater than zero.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ============================================================
    # VALIDATE PAYMENT DATE
    # ============================================================

    if not payment_date:

        messages.error(
            request,
            "Please enter the payment date.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ============================================================
    # VALIDATE PAYMENT METHOD
    # ============================================================

    if not payment_method:

        messages.error(
            request,
            "Please select a payment method.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ============================================================
    # CHECK DUPLICATE PAYMENT REFERENCE
    # ============================================================

    if payment_reference:

        duplicate = WelfarePayment.objects.filter(
            payment_reference=payment_reference
        ).exists()

        if duplicate:

            messages.error(
                request,
                "This payment reference already exists.",
            )

            return redirect(
                "welfare:detail",
                pk=case.pk,
            )

    # ============================================================
    # CALCULATE TOTAL ALREADY PAID
    # ============================================================

    total_paid_before = (
        WelfarePayment.objects
        .filter(case=case)
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    # ============================================================
    # CALCULATE REMAINING APPROVED AMOUNT
    # ============================================================

    remaining_amount = (
        case.amount_approved
        - total_paid_before
    )

    # ------------------------------------------------------------
    # Already fully paid
    # ------------------------------------------------------------

    if remaining_amount <= Decimal("0"):

        messages.error(
            request,
            "This welfare request has already been fully paid.",
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ------------------------------------------------------------
    # Payment cannot exceed remaining balance
    # ------------------------------------------------------------

    if amount > remaining_amount:

        messages.error(
            request,
            (
                "Payment exceeds the remaining approved amount "
                f"of ₦{remaining_amount:,.2f}."
            ),
        )

        return redirect(
            "welfare:detail",
            pk=case.pk,
        )

    # ============================================================
    # CREATE FINANCE EXPENSE + WELFARE PAYMENT
    # ============================================================

    with transaction.atomic():

        # --------------------------------------------------------
        # Welfare finance category
        # --------------------------------------------------------

        welfare_category, created = (
            ExpenseCategory.objects.get_or_create(
                name="Welfare",
                defaults={
                    "description": (
                        "Expenses relating to member welfare "
                        "assistance and support."
                    ),
                    "is_active": True,
                },
            )
        )

        # --------------------------------------------------------
        # Member name
        # --------------------------------------------------------

        member_name = (
            case.member.get_full_name()
            or case.member.username
        )

        # --------------------------------------------------------
        # Create finance expense
        # --------------------------------------------------------

        expense = Expense.objects.create(

            category=welfare_category,

            amount=amount,

            description=(
                f"Welfare payment for "
                f"{member_name}: "
                f"{case.title}"
            ),

            payment_method=payment_method or "OTHER",

            transaction_date=payment_date,

            reference=payment_reference,

            payee=member_name,

            recorded_by=request.user,
        )

        # --------------------------------------------------------
        # Create welfare payment
        # --------------------------------------------------------

        WelfarePayment.objects.create(

            case=case,

            amount=amount,

            payment_date=payment_date,

            payment_reference=payment_reference,

            payment_method=payment_method,

            notes=notes,

            recorded_by=request.user,

            finance_expense=expense,
        )

        # ========================================================
        # CALCULATE NEW TOTAL PAID
        # ========================================================

        total_paid_after = (
            WelfarePayment.objects
            .filter(case=case)
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or Decimal("0")
        )

        # ========================================================
        # UPDATE CASE STATUS
        # ========================================================

        if total_paid_after >= case.amount_approved:

            case.status = WelfareCase.Status.PAID

            case.paid_at = timezone.now()

        else:

            # Payment has been made but the full approved
            # amount has not yet been paid.

            case.status = (
                WelfareCase.Status.PARTIALLY_APPROVED
            )

            case.paid_at = None

        # --------------------------------------------------------
        # Save case
        # --------------------------------------------------------

        case.save(
            update_fields=[
                "status",
                "paid_at",
                "updated_at",
            ]
        )

    # ============================================================
    # SUCCESS MESSAGE
    # ============================================================

    if case.status == WelfareCase.Status.PAID:

        messages.success(
            request,
            (
                f"Welfare payment of ₦{amount:,.2f} "
                "has been recorded successfully. "
                "The welfare request has now been fully paid."
            ),
        )

    else:

        remaining_after_payment = (
            case.amount_approved
            - total_paid_after
        )

        messages.success(
            request,
            (
                f"Welfare payment of ₦{amount:,.2f} "
                "has been recorded successfully. "
                f"Remaining approved balance: "
                f"₦{remaining_after_payment:,.2f}."
            ),
        )

    # ============================================================
    # REDIRECT
    # ============================================================

    return redirect(
        "welfare:detail",
        pk=case.pk,
    )