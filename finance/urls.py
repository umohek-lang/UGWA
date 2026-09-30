from django.urls import path

from . import views


app_name = "finance"


urlpatterns = [

    path(
        "",
        views.finance_dashboard,
        name="dashboard"
    ),

    # -------------------------
    # INCOME
    # -------------------------

    path(
        "income/",
        views.income_list,
        name="income_list"
    ),

    path(
        "income/add/",
        views.income_create,
        name="income_create"
    ),

    # -------------------------
    # EXPENSES
    # -------------------------

    path(
        "expenses/",
        views.expense_list,
        name="expense_list"
    ),

    path(
        "expenses/add/",
        views.expense_create,
        name="expense_create"
    ),

    # -------------------------
    # REPORTS
    # -------------------------

    path(
        "reports/",
        views.financial_report,
        name="report"
    ),

    path(
        "reports/monthly/",
        views.monthly_report,
        name="monthly_report"
    ),
]