from django.urls import path
from . import views
from .views import home


app_name = "association"

urlpatterns = [
    path("", home, name="home"),

      path(
        "about/",
        views.about,
        name="about"
    ),


    path(
    "constitution/",
    views.constitution,
    name="constitution"
),
]