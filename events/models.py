from django.conf import settings
from django.db import models


class Event(models.Model):

    class EventType(models.TextChoices):

        MEETING = "MEETING", "Meeting"
        CONFERENCE = "CONFERENCE", "Conference"
        SEMINAR = "SEMINAR", "Seminar"
        WORKSHOP = "WORKSHOP", "Workshop"
        AGM = "AGM", "Annual General Meeting"
        SOCIAL = "SOCIAL", "Social Event"
        OTHER = "OTHER", "Other"

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True
    )

    description = models.TextField()

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        default=EventType.OTHER
    )

    event_image = models.ImageField(
        upload_to="events/",
        blank=True,
        null=True
    )

    venue = models.CharField(
        max_length=255
    )

    address = models.TextField(
        blank=True
    )

    start_date = models.DateTimeField()

    end_date = models.DateTimeField(
        blank=True,
        null=True
    )

    registration_required = models.BooleanField(
        default=False
    )

    registration_deadline = models.DateTimeField(
        blank=True,
        null=True
    )

    capacity = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    is_published = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_events"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "start_date"
        ]

    def __str__(self):

        return self.title


class EventRegistration(models.Model):

    class Status(models.TextChoices):

        REGISTERED = "REGISTERED", "Registered"
        ATTENDED = "ATTENDED", "Attended"
        CANCELLED = "CANCELLED", "Cancelled"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED
    )

    registered_at = models.DateTimeField(
        auto_now_add=True
    )

    attended_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["event", "member"],
                name="unique_event_member_registration"
            )
        ]

        ordering = [
            "-registered_at"
        ]

    def __str__(self):

        return (
            f"{self.member.username} - {self.event.title}"
        )