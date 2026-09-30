from django.urls import path
from . import webhooks
from . import views


app_name = "payments"


urlpatterns = [

    path(
        "",
        views.invoices,
        name="invoices"
    ),

    path(
        "history/",
        views.payment_history,
        name="history"
    ),

    path(
        "invoice/<str:invoice_number>/",
        views.invoice_detail,
        name="invoice_detail"
    ),

    path(
        "invoice/<str:invoice_number>/pay/",
        views.pay_invoice,
        name="pay_invoice"
    ),

    path(
        "paystack/callback/",
        views.paystack_callback,
        name="paystack_callback"
    ),

      path(
        "paystack/webhook/",
        webhooks.paystack_webhook,
        name="paystack_webhook"
    ),

    path(
    "receipt/<str:receipt_number>/",
    views.payment_receipt,
    name="receipt"
),

path(
    "membership/",
    views.membership_dashboard,
    name="membership_dashboard"
),

path(
    "membership/card/",
    views.membership_card,
    name="membership_card"
),



path(
    "dues/types/",
    views.dues_type_list,
    name="dues_type_list"
),

path(
    "dues/types/add/",
    views.dues_type_create,
    name="dues_type_create"
),

path(
    "dues/schedules/",
    views.dues_schedule_list,
    name="dues_schedule_list"
),

path(
    "dues/schedules/add/",
    views.dues_schedule_create,
    name="dues_schedule_create"
),

path(
    "dues/schedules/<int:schedule_id>/invoice/",
    views.generate_invoice,
    name="generate_invoice"
),

path(
    "receipts/<str:receipt_number>/",
    views.receipt_detail,
    name="receipt_detail",
),

path(
    "membership/management/",
    views.membership_officer_dashboard,
    name="membership_officer_dashboard"
),

path(
    "membership/member/<int:member_id>/",
    views.member_detail,
    name="member_detail",
),

path(
    "membership/member/<int:member_id>/edit/",
    views.member_edit,
    name="member_edit",
),

path(
    "membership/verify/<str:membership_code>/",
    views.verify_membership,
    name="verify_membership",
),


path(
    "membership/<int:member_id>/suspend/",
    views.suspend_member,
    name="suspend_member",
),

path(
    "membership/<int:member_id>/reactivate/",
    views.reactivate_member,
    name="reactivate_member",
),

# path(
#     "membership/management/",
#     views.membership_management,
#     name="membership_management"
# ),

]