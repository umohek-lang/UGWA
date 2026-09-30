from django.shortcuts import render

from .utils import get_association


def home(request):

    association = get_association()

    return render(
        request,
        "association/home.html",
        {
            "association": association,
        }
    )

def about(request):

    association = get_association()

    return render(
        request,
        "association/about.html",
        {
            "association": association,
        }
    )

def constitution(request):

    association = get_association()

    return render(
        request,
        "association/constitution.html",
        {
            "association": association,
        }
    )