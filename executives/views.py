from django.shortcuts import render

from .models import Executive


def leadership(request):

    executives = Executive.objects.filter(
        is_active=True
    )

    return render(
        request,
        "executives/leadership.html",
        {
            "executives": executives,
        }
    )