from django.urls import path

from . import views


app_name = "documents"


urlpatterns = [

    path(
        "",
        views.document_list,
        name="list"
    ),

    path(
        "<slug:slug>/",
        views.document_detail,
        name="detail"
    ),

    path(
        "<slug:slug>/download/",
        views.document_download,
        name="download"
    ),

]