from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


MEMBERSHIP_ROLES = [
    "SUPER_ADMIN",
    "MEMBERSHIP_OFFICER",
]


def membership_officer_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if (
            request.user.is_superuser
            or request.user.role in MEMBERSHIP_ROLES
        ):
            return view_func(
                request,
                *args,
                **kwargs
            )

        messages.error(
            request,
            "You do not have permission to access Membership Management."
        )

        return redirect("dashboard:home")

    return wrapper