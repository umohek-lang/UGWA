from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta


class User(AbstractUser):

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Administrator"
        PRESIDENT = "PRESIDENT", "President"
        VICE_PRESIDENT = "VICE_PRESIDENT", "Vice President"
        SECRETARY = "SECRETARY", "General Secretary"
        ASSISTANT_SECRETARY = "ASSISTANT_SECRETARY", "Assistant Secretary"
        TREASURER = "TREASURER", "Treasurer"
        FINANCIAL_SECRETARY = "FINANCIAL_SECRETARY", "Financial Secretary"
        PRO = "PRO", "Public Relations Officer"
        MEMBERSHIP_OFFICER = "MEMBERSHIP_OFFICER", "Membership Officer"
        WELFARE_OFFICER = "WELFARE_OFFICER", "Welfare Officer"
        EVENT_OFFICER = "EVENT_OFFICER", "Event Officer"
        BRANCH_ADMIN = "BRANCH_ADMIN", "Branch Administrator"
        MEMBER = "MEMBER", "Member"

    class MembershipStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        EXPIRED = "EXPIRED", "Expired"
        INACTIVE = "INACTIVE", "Inactive"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )
    photo = models.ImageField(
    upload_to="members/photos/",
    blank=True,
    null=True,
)
    is_approved = models.BooleanField(
        default=False
    )

    membership_code = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
    )

    membership_date = models.DateField(
        null=True,
        blank=True,
    )

    membership_expiry_date = models.DateField(
    null=True,
    blank=True
)

    membership_status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if(
            is_new and self.membership_date is None
            and self.role == self.Role.MEMBER
        ):
            self.membership_date = date.today()
        super().save(*args, **kwargs)

        if(
            not self.membership_code
            and self.role == self.Role.MEMBER
        ):
             self.membership_code = (
            f"UGMWA-{self.membership_date.year}-{self.pk:06d}"
        )

        super().save(
            update_fields=["membership_code"]
        )

    def __str__(self):
        return self.username


    