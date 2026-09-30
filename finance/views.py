from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import finance_required
from .forms import IncomeForm, ExpenseForm
from .models import (
    Expense,
    ExpenseCategory,
    Income,
    IncomeCategory,
)


@login_required
@finance_required
def finance_dashboard(request):

    today = date.today()

    current_year = today.year
    current_month = today.month

    # -------------------------------------------------
    # Current year
    # -------------------------------------------------

    yearly_income = (
        Income.objects
        .filter(
            transaction_date__year=current_year
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    yearly_expenses = (
        Expense.objects
        .filter(
            transaction_date__year=current_year
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    yearly_balance = (
        yearly_income - yearly_expenses
    )

    # -------------------------------------------------
    # Current month
    # -------------------------------------------------

    monthly_income = (
        Income.objects
        .filter(
            transaction_date__year=current_year,
            transaction_date__month=current_month
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    monthly_expenses = (
        Expense.objects
        .filter(
            transaction_date__year=current_year,
            transaction_date__month=current_month
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    # -------------------------------------------------
    # Today's transactions
    # -------------------------------------------------

    today_income = (
        Income.objects
        .filter(
            transaction_date=today
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    today_expenses = (
        Expense.objects
        .filter(
            transaction_date=today
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    # -------------------------------------------------
    # Welfare expenses
    # -------------------------------------------------

    welfare_expenses = (
        Expense.objects
        .filter(
            category__name__iexact="Welfare"
        )
        .aggregate(
            total=Sum("amount")
        )
        .get("total")
        or Decimal("0")
    )

    # -------------------------------------------------
    # Recent income
    # -------------------------------------------------

    recent_income = (
        Income.objects
        .select_related(
            "category",
            "recorded_by"
        )
        .order_by(
            "-transaction_date",
            "-created_at"
        )[:5]
    )

    # -------------------------------------------------
    # Recent expenses
    # -------------------------------------------------

    recent_expenses = (
        Expense.objects
        .select_related(
            "category",
            "recorded_by"
        )
        .order_by(
            "-transaction_date",
            "-created_at"
        )[:5]
    )

    # -------------------------------------------------
    # Monthly summary
    # -------------------------------------------------

    monthly_summary = []

    for month in range(1, 13):

        income = (
            Income.objects
            .filter(
                transaction_date__year=current_year,
                transaction_date__month=month
            )
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or Decimal("0")
        )

        expense = (
            Expense.objects
            .filter(
                transaction_date__year=current_year,
                transaction_date__month=month
            )
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or Decimal("0")
        )

        monthly_summary.append(
            {
                "month": date(
                    current_year,
                    month,
                    1
                ).strftime("%B"),

                "income": income,

                "expense": expense,

                "balance": (
                    income - expense
                ),
            }
        )

    context = {
        "today": today,
        "current_year": current_year,

        "yearly_income": yearly_income,
        "yearly_expenses": yearly_expenses,
        "yearly_balance": yearly_balance,

        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,

        "today_income": today_income,
        "today_expenses": today_expenses,

        "welfare_expenses": welfare_expenses,

        "recent_income": recent_income,
        "recent_expenses": recent_expenses,

        "monthly_summary": monthly_summary,
    }

    return render(
        request,
        "finance/dashboard1.html",
        context
    )


@login_required
@finance_required
def financial_report(request):

    incomes = (
        Income.objects
        .select_related(
            "category",
            "recorded_by"
        )
        .order_by(
            "-transaction_date",
            "-created_at"
        )
    )

    expenses = (
        Expense.objects
        .select_related(
            "category",
            "recorded_by"
        )
        .order_by(
            "-transaction_date",
            "-created_at"
        )
    )

    # -------------------------------------------------
    # Filter values
    # -------------------------------------------------

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    income_category = request.GET.get(
        "income_category"
    )

    expense_category = request.GET.get(
        "expense_category"
    )

    # -------------------------------------------------
    # Date filter
    # -------------------------------------------------

    if start_date:

        incomes = incomes.filter(
            transaction_date__gte=start_date
        )

        expenses = expenses.filter(
            transaction_date__gte=start_date
        )

    if end_date:

        incomes = incomes.filter(
            transaction_date__lte=end_date
        )

        expenses = expenses.filter(
            transaction_date__lte=end_date
        )

    # -------------------------------------------------
    # Category filter
    # -------------------------------------------------

    if income_category:

        incomes = incomes.filter(
            category_id=income_category
        )

    if expense_category:

        expenses = expenses.filter(
            category_id=expense_category
        )

    # -------------------------------------------------
    # Totals
    # -------------------------------------------------

    total_income = (
        incomes.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0")
    )

    total_expenses = (
        expenses.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0")
    )

    net_balance = (
        total_income - total_expenses
    )

    income_categories = (
        IncomeCategory.objects
        .filter(
            is_active=True
        )
        .order_by("name")
    )

    expense_categories = (
        ExpenseCategory.objects
        .filter(
            is_active=True
        )
        .order_by("name")
    )

    context = {
        "incomes": incomes,
        "expenses": expenses,

        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,

        "income_categories": income_categories,
        "expense_categories": expense_categories,

        "selected_start_date": (
            start_date or ""
        ),

        "selected_end_date": (
            end_date or ""
        ),

        "selected_income_category": (
            income_category or ""
        ),

        "selected_expense_category": (
            expense_category or ""
        ),
    }

    return render(
        request,
        "finance/financial_report.html",
        context
    )


@login_required
@finance_required
def monthly_report(request):

    current_year = date.today().year

    selected_year = request.GET.get(
        "year"
    )

    if selected_year:

        try:

            selected_year = int(
                selected_year
            )

        except ValueError:

            selected_year = current_year

    else:

        selected_year = current_year

    monthly_data = []

    for month in range(1, 13):

        income_total = (
            Income.objects
            .filter(
                transaction_date__year=selected_year,
                transaction_date__month=month
            )
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or Decimal("0")
        )

        expense_total = (
            Expense.objects
            .filter(
                transaction_date__year=selected_year,
                transaction_date__month=month
            )
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or Decimal("0")
        )

        monthly_data.append(
            {
                "month": date(
                    selected_year,
                    month,
                    1
                ).strftime("%B"),

                "income": income_total,

                "expenses": expense_total,

                "balance": (
                    income_total
                    - expense_total
                ),
            }
        )

    context = {
        "monthly_data": monthly_data,
        "selected_year": selected_year,
    }

    return render(
        request,
        "finance/monthly_report.html",
        context
    )


@login_required
@finance_required
def income_create(request):

    if request.method == "POST":

        form = IncomeForm(
            request.POST
        )

        if form.is_valid():

            income = form.save(
                commit=False
            )

            income.recorded_by = request.user

            income.save()

            messages.success(
                request,
                "Income has been recorded successfully."
            )

            return redirect(
                "finance:income_list"
            )

    else:

        form = IncomeForm()

    return render(
        request,
        "finance/income_form.html",
        {
            "form": form,
            "page_title": "Record Income",
        }
    )


@login_required
@finance_required
def expense_create(request):

    if request.method == "POST":

        form = ExpenseForm(
            request.POST
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.recorded_by = request.user

            expense.save()

            messages.success(
                request,
                "Expense has been recorded successfully."
            )

            return redirect(
                "finance:expense_list"
            )

    else:

        form = ExpenseForm()

    return render(
        request,
        "finance/expense_form.html",
        {
            "form": form,
            "page_title": "Record Expense",
        }
    )


@login_required
@finance_required
def income_list(request):

    incomes = (
        Income.objects
        .select_related(
            "category",
            "recorded_by"
        )
        .order_by(
            "-transaction_date",
            "-created_at"
        )
    )

    return render(
        request,
        "finance/income_list.html",
        {
            "incomes": incomes,
        }
    )


@login_required
@finance_required
def expense_list(request):

    expenses = (
        Expense.objects
        .select_related(
            "category",
            "recorded_by"
        )
        .order_by(
            "-transaction_date",
            "-created_at"
        )
    )

    return render(
        request,
        "finance/expense_list.html",
        {
            "expenses": expenses,
        }
    )
