from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MemberProfileForm
from .models import MemberProfile


@login_required
def profile(request):

    member_profile, created = MemberProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "members/profile.html",
        {
            "member_profile": member_profile,
        }
    )


@login_required
def profile_edit(request):

    member_profile, created = MemberProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = MemberProfileForm(
            request.POST,
            request.FILES,
            instance=member_profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("members:profile")

    else:

        form = MemberProfileForm(
            instance=member_profile
        )

    return render(
        request,
        "members/profile_edit.html",
        {
            "form": form,
            "member_profile": member_profile,
        }
    )