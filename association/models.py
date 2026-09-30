from django.db import models


class AssociationProfile(models.Model):

    name = models.CharField(
        max_length=200,
        default="My Association"
    )

    short_name = models.CharField(
        max_length=50,
        blank=True
    )

    logo = models.ImageField(
        upload_to="association/logo/",
        blank=True,
        null=True
    )

    cover_image = models.ImageField(
        upload_to="association/cover/",
        blank=True,
        null=True
    )

    slogan = models.CharField(
        max_length=255,
        blank=True
    )

    history = models.TextField(
        blank=True
    )

    mission = models.TextField(
        blank=True
    )

    vision = models.TextField(
        blank=True
    )

    objectives = models.TextField(
        blank=True
    )

    constitution = models.TextField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    facebook = models.URLField(
        blank=True
    )

    twitter = models.URLField(
        blank=True
    )

    instagram = models.URLField(
        blank=True
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

    def __str__(self):
        return self.name