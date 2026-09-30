from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Event, EventRegistration


def event_list(request):

    now = timezone.now()

    upcoming_events = Event.objects.filter(
        is_published=True,
        start_date__gte=now
    ).order_by("start_date")

    past_events = Event.objects.filter(
        is_published=True,
        start_date__lt=now
    ).order_by("-start_date")

    return render(
        request,
        "events/event_list.html",
        {
            "upcoming_events": upcoming_events,
            "past_events": past_events,
        }
    )


def event_detail(request, slug):

    event = get_object_or_404(
        Event,
        slug=slug,
        is_published=True
    )

    registration_count = EventRegistration.objects.filter(
        event=event,
        status=EventRegistration.Status.REGISTERED
    ).count()

    user_registered = False

    if request.user.is_authenticated:

        user_registered = EventRegistration.objects.filter(
            event=event,
            member=request.user
        ).exclude(
            status=EventRegistration.Status.CANCELLED
        ).exists()

    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "registration_count": registration_count,
            "user_registered": user_registered,
        }
    )


@login_required
def register_event(request, slug):

    if request.method != "POST":
        return redirect("events:detail", slug=slug)

    event = get_object_or_404(
        Event,
        slug=slug,
        is_published=True
    )

    if not event.registration_required:

        messages.info(
            request,
            "Registration is not required for this event."
        )

        return redirect(
            "events:detail",
            slug=slug
        )

    if event.registration_deadline:

        if timezone.now() > event.registration_deadline:

            messages.error(
                request,
                "Registration for this event has closed."
            )

            return redirect(
                "events:detail",
                slug=slug
            )

    if event.capacity:

        registration_count = EventRegistration.objects.filter(
            event=event,
            status=EventRegistration.Status.REGISTERED
        ).count()

        if registration_count >= event.capacity:

            messages.error(
                request,
                "This event has reached its registration capacity."
            )

            return redirect(
                "events:detail",
                slug=slug
            )

    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        member=request.user,
        defaults={
            "status": EventRegistration.Status.REGISTERED
        }
    )

    if not created:

        if registration.status == EventRegistration.Status.CANCELLED:

            registration.status = (
                EventRegistration.Status.REGISTERED
            )

            registration.save(
                update_fields=["status"]
            )

            messages.success(
                request,
                "You have been registered for the event."
            )

        else:

            messages.info(
                request,
                "You are already registered for this event."
            )

    else:

        messages.success(
            request,
            "You have successfully registered for this event."
        )

    return redirect(
        "events:detail",
        slug=slug
    )