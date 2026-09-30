from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def membership_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if request.user.is_superuser:
            return view_func(
                request,
                *args,
                **kwargs
            )

        if not request.user.membership_code:

            messages.error(
                request,
                (
                    "Your membership has not yet been "
                    "assigned a membership code."
                )
            )

            return redirect(
                "payments:membership_dashboard"
            )

        if request.user.membership_status != "ACTIVE":

            messages.error(
                request,
                (
                    "Your membership is not currently active. "
                    "Please contact the Membership Officer."
                )
            )

            return redirect(
                "payments:membership_dashboard"
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper