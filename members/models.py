from django.conf import settings
from django.db import models


class MembershipCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    annual_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
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

    def __str__(self):
        return self.name


class MemberProfile(models.Model):

    class Gender(models.TextChoices):

        MALE = "MALE", "Male"

        FEMALE = "FEMALE", "Female"

        OTHER = "OTHER", "Other"


    class Status(models.TextChoices):

        PENDING = "PENDING", "Pending"

        ACTIVE = "ACTIVE", "Active"

        SUSPENDED = "SUSPENDED", "Suspended"

        INACTIVE = "INACTIVE", "Inactive"

        EXPIRED = "EXPIRED", "Expired"


    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile"
    )

    membership_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    profile_photo = models.ImageField(
        upload_to="members/photos/",
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    lga = models.CharField(
        max_length=100,
        blank=True
    )

    occupation = models.CharField(
        max_length=150,
        blank=True
    )

    organization = models.CharField(
        max_length=200,
        blank=True
    )

    qualification = models.CharField(
        max_length=200,
        blank=True
    )

    membership_category = models.ForeignKey(
        MembershipCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    joined_date = models.DateField(
        blank=True,
        null=True
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return (
            self.membership_number
            or self.user.get_full_name()
            or self.user.username
        )


    def generate_membership_number(self):

        if not self.membership_number and self.pk:

            self.membership_number = f"ASS-{self.pk:06d}"

            self.save(
                update_fields=["membership_number"]
            )

        return self.membership_number