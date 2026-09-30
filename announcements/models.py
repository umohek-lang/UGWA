from django.conf import settings
from django.db import models


class Announcement(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True
    )

    content = models.TextField()

    image = models.ImageField(
        upload_to="announcements/",
        blank=True,
        null=True
    )

    is_published = models.BooleanField(
        default=True
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_announcements"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-published_at",
            "-created_at"
        ]

    def __str__(self):

        return self.title