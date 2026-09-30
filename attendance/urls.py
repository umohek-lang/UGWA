from django.urls import path

from . import views


app_name = "attendance"


urlpatterns = [

    path(
        "",
        views.attendance_list,
        name="list"
    ),

    path(
        "my/",
        views.my_attendance,
        name="my"
    ),

    path(
        "<int:pk>/",
        views.attendance_detail,
        name="detail"
    ),

    path(
        "<int:pk>/mark/",
        views.mark_attendance,
        name="mark"
    ),

]