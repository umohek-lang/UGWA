from django.db import models


class Executive(models.Model):

    position = models.CharField(
        max_length=150
    )

    full_name = models.CharField(
        max_length=200
    )

    photo = models.ImageField(
        upload_to="executives/",
        blank=True,
        null=True
    )

    biography = models.TextField(
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "display_order",
            "position",
        ]

    def __str__(self):

        return f"{self.position} - {self.full_name}"