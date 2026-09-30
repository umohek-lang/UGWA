from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):

    # If the user is already logged in,
    # send them to the dashboard.
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                "Registration successful. Your account is awaiting approval."
            )

            # Send the user to the login page
            # after successful registration.
            return redirect("accounts:login")

    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


def login_view(request):

    # If the user is already logged in,
    # don't show the login page again.
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate the username and password.
        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            # Check whether the account has been approved.
            # Superusers are allowed to log in even if
            # is_approved is False.
            if not user.is_approved and not user.is_superuser:

                messages.warning(
                    request,
                    "Your account has not yet been approved."
                )

                return redirect("accounts:login")

            # Log the user into Django.
            login(request, user)

            messages.success(
                request,
                "Welcome back!"
            )

            # IMPORTANT:
            # Your dashboard URL is namespaced as dashboard:home.
            return redirect("dashboard:home")

        # Authentication failed.
        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html",
    )


def logout_view(request):

    # Log the user out.
    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    # Send the user back to the dashboard/home page.
    return redirect("dashboard:home")
