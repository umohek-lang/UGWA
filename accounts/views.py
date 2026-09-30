from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import RegistrationForm


def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            # -------------------------------------------------
            # CREATE USER
            # -------------------------------------------------

            user = form.save()

            # Automatically approve membership
            user.is_approved = True

            # User must activate account through email
            user.is_active = False

            # Set membership status
            if user.role == user.Role.MEMBER:
                user.membership_status = (
                    user.MembershipStatus.ACTIVE
                )

            user.save()

            # -------------------------------------------------
            # CREATE ACTIVATION LINK
            # -------------------------------------------------

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(user)

            activation_url = request.build_absolute_uri(
                reverse(
                    "accounts:activate",
                    kwargs={
                        "uid": uid,
                        "token": token,
                    },
                )
            )

            # -------------------------------------------------
            # EMAIL CONTENT
            # -------------------------------------------------

            subject = "Activate Your UGMWA Membership Account"

            full_name = (
                user.get_full_name()
                or user.username
            )

            # Plain-text email
            text_message = f"""
Dear {full_name},

Welcome to UGWU MBAISE WOMEN'S ASSOCIATION ABUJA (UGMWA).

Your membership registration has been completed successfully.

Your membership has been automatically approved.

Membership Code:
{user.membership_code}

Please activate your account using the link below:

{activation_url}

After activation, you can log in using the username and password
you created during registration.

If you did not create this account, please ignore this email.

Regards,

UGMWA Administration
PEACE, UNITY & PROGRESS
"""

            # HTML email
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Activate Your UGMWA Account</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f4f7f5;
    font-family: Arial, Helvetica, sans-serif;
">

    <div style="
        max-width: 600px;
        margin: 40px auto;
        background: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    ">

        <!-- HEADER -->

        <div style="
            background-color: #0b5d3b;
            padding: 30px;
            text-align: center;
            color: #ffffff;
        ">

            <h1 style="
                margin: 0;
                font-size: 26px;
            ">
                UGMWA
            </h1>

            <p style="
                margin: 8px 0 0;
                font-size: 14px;
            ">
                UGWU MBAISE WOMEN'S ASSOCIATION ABUJA
            </p>

        </div>


        <!-- BODY -->

        <div style="
            padding: 35px;
            color: #333333;
        ">

            <h2 style="
                color: #0b5d3b;
                margin-top: 0;
            ">
                Welcome, {full_name}!
            </h2>

            <p>
                Your membership registration has been completed
                successfully.
            </p>

            <p>
                Your membership has been
                <strong>automatically approved</strong>.
            </p>


            <!-- MEMBERSHIP CODE -->

            <div style="
                background-color: #f4f7f5;
                border-left: 5px solid #d4af37;
                padding: 18px;
                margin: 25px 0;
            ">

                <p style="
                    margin: 0 0 6px;
                    font-size: 13px;
                    color: #666666;
                ">
                    Your Membership Code
                </p>

                <p style="
                    margin: 0;
                    font-size: 22px;
                    font-weight: bold;
                    color: #0b5d3b;
                ">
                    {user.membership_code}
                </p>

            </div>


            <p>
                To complete your registration, please activate
                your account by clicking the button below.
            </p>


            <!-- ACTIVATION BUTTON -->

            <div style="
                text-align: center;
                margin: 30px 0;
            ">

                <a href="{activation_url}"
                   style="
                       display: inline-block;
                       background-color: #0b5d3b;
                       color: #ffffff;
                       text-decoration: none;
                       padding: 14px 30px;
                       border-radius: 6px;
                       font-size: 16px;
                       font-weight: bold;
                   ">

                    ACTIVATE MY ACCOUNT

                </a>

            </div>


            <p style="
                font-size: 14px;
                color: #666666;
            ">
                If the button does not work, copy and paste the
                following link into your browser:
            </p>


            <p style="
                font-size: 13px;
                word-break: break-all;
            ">

                <a href="{activation_url}">
                    {activation_url}
                </a>

            </p>


            <p>
                After activation, you can log in using the
                username and password you created during
                registration.
            </p>


            <p>
                If you did not create this account, please
                ignore this email.
            </p>


            <p style="
                margin-top: 30px;
            ">

                Regards,<br>

                <strong>UGMWA Administration</strong>

            </p>

        </div>


        <!-- FOOTER -->

        <div style="
            background-color: #0b5d3b;
            padding: 18px;
            text-align: center;
            color: #ffffff;
            font-size: 13px;
        ">

            PEACE, UNITY & PROGRESS

        </div>

    </div>

</body>
</html>
"""

            # -------------------------------------------------
            # SEND EMAIL
            # -------------------------------------------------

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=None,
                to=[user.email],
            )

            email.attach_alternative(
                html_message,
                "text/html",
            )

            email.send(
                fail_silently=False
            )


            # -------------------------------------------------
            # SAVE ACTIVATION URL FOR LOGIN PAGE
            # -------------------------------------------------

            request.session["activation_url"] = activation_url


            # -------------------------------------------------
            # SUCCESS MESSAGE
            # -------------------------------------------------

            messages.success(
                request,
                "Registration successful. Your membership has "
                "been approved automatically. Please check your "
                "email to activate your account."
            )

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


# ============================================================
# ACTIVATE ACCOUNT
# ============================================================

def activate_account(request, uid, token):

    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:

        uid = force_str(
            urlsafe_base64_decode(uid)
        )

        user = User.objects.get(
            pk=uid
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):

        messages.error(
            request,
            "Invalid activation link."
        )

        return redirect("accounts:login")


    # Check activation token

    if not default_token_generator.check_token(
        user,
        token
    ):

        messages.error(
            request,
            "This activation link is invalid or has expired."
        )

        return redirect("accounts:login")


    # Activate account

    user.is_active = True
    user.is_approved = True

    if user.role == user.Role.MEMBER:

        user.membership_status = (
            user.MembershipStatus.ACTIVE
        )

    user.save()


    messages.success(
        request,
        "Your account has been activated successfully. "
        "You can now log in."
    )


    return redirect("accounts:login")


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:home")


    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")


        user = authenticate(
            request,
            username=username,
            password=password,
        )


        if user is not None:


            # Check approval

            if not user.is_approved and not user.is_superuser:

                messages.warning(
                    request,
                    "Your account has not yet been approved."
                )

                return redirect("accounts:login")


            # Check activation

            if not user.is_active and not user.is_superuser:

                messages.warning(
                    request,
                    "Your account has not been activated. "
                    "Please check your email and click the "
                    "activation link."
                )

                return redirect("accounts:login")


            # Login

            login(
                request,
                user
            )


            messages.success(
                request,
                "Welcome back!"
            )


            return redirect(
                "dashboard:home"
            )


        messages.error(
            request,
            "Invalid username or password."
        )


    # -------------------------------------------------
    # GET ACTIVATION URL FROM SESSION
    # -------------------------------------------------

    activation_url = request.session.pop(
        "activation_url",
        None
    )


    return render(
        request,
        "accounts/login.html",
        {
            "activation_url": activation_url,
        },
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)


    messages.success(
        request,
        "You have been logged out successfully."
    )


    return redirect(
        "dashboard:home"
    )
