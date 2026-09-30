from django.urls import path

from . import views


app_name = "welfare"


urlpatterns = [

    path(
        "",
        views.case_list,
        name="list"
    ),

    path(
        "my/",
        views.my_cases,
        name="my"
    ),

    path(
        "submit/",
        views.case_create,
        name="create"
    ),

    path(
        "<int:pk>/",
        views.case_detail,
        name="detail"
    ),

    path(
        "<int:pk>/review/",
        views.review_case,
        name="review"
    ),

    path(
    "<int:pk>/payment/",
    views.record_payment,
    name="record_payment"
),

]