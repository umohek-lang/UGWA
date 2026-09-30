from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from payments.models import Invoice


@login_required
def dashboard(request):

    user = request.user

    total_outstanding = 0

    if not user.is_superuser:

        invoices = Invoice.objects.filter(
            member=user
        ).exclude(
            status=Invoice.Status.CANCELLED
        )

        total_outstanding = sum(
            invoice.balance
            for invoice in invoices
        )

    context = {
        "total_outstanding": total_outstanding,
    }

    # Super Admin
    if user.is_superuser or user.role == user.Role.SUPER_ADMIN:

        return render(
            request,
            "dashboard/admin_dashboard.html",
            context
        )

    # Executive
    if user.role in [
        user.Role.PRESIDENT,
        user.Role.VICE_PRESIDENT,
        user.Role.SECRETARY,
        user.Role.ASSISTANT_SECRETARY,
        user.Role.PRO,
    ]:

        return render(
            request,
            "dashboard/executive_dashboard.html",
            context
        )

    # Finance
    if user.role in [
        user.Role.TREASURER,
        user.Role.FINANCIAL_SECRETARY,
    ]:

        return redirect(
            "finance:dashboard"
        )

    # Membership Officer
    if user.role == user.Role.MEMBERSHIP_OFFICER:

        return render(
            request,
            "dashboard/membership_dashboard.html",
            context
        )

    # Welfare Officer
    if user.role == user.Role.WELFARE_OFFICER:

        return render(
            request,
            "dashboard/welfare_dashboard.html",
            context
        )

    # Event Officer
    if user.role == user.Role.EVENT_OFFICER:

        return render(
            request,
            "dashboard/events_dashboard.html",
            context
        )

    # Branch Admin
    if user.role == user.Role.BRANCH_ADMIN:

        return render(
            request,
            "dashboard/branch_dashboard.html",
            context
        )

    # Normal Member
    return render(
        request,
        "dashboard/member_dashboard.html",
        context
    )


@login_required
def member_dashboard(request):

    return render(
        request,
        "dashboard/member_dashboard.html"
    )