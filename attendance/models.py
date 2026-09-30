from django.conf import settings
from django.db import models


class AttendanceSession(models.Model):

    class SessionType(models.TextChoices):
        MEETING = "MEETING", "Meeting"
        EVENT = "EVENT", "Event"
        AGM = "AGM", "Annual General Meeting"
        CONFERENCE = "CONFERENCE", "Conference"
        TRAINING = "TRAINING", "Training"
        OTHER = "OTHER", "Other"

    title = models.CharField(
        max_length=200
    )

    session_type = models.CharField(
        max_length=30,
        choices=SessionType.choices,
        default=SessionType.MEETING
    )

    description = models.TextField(
        blank=True
    )

    date = models.DateField()

    start_time = models.TimeField(
        blank=True,
        null=True
    )

    end_time = models.TimeField(
        blank=True,
        null=True
    )

    venue = models.CharField(
        max_length=255,
        blank=True
    )

    is_open = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_attendance_sessions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-date",
            "-start_time"
        ]

    def __str__(self):
        return self.title


class AttendanceRecord(models.Model):

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        EXCUSED = "EXCUSED", "Excused"

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records"
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT
    )

    check_in = models.DateTimeField(
        blank=True,
        null=True
    )

    check_out = models.DateTimeField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True
    )

    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance_records"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "session",
                    "member"
                ],
                name="unique_attendance_session_member"
            )
        ]

    def __str__(self):
        return (
            f"{self.member.username} - "
            f"{self.session.title}"
        )