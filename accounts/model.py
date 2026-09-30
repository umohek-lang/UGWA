def save(self, *args, **kwargs):
    is_new = self.pk is None

    if (
        is_new
        and self.membership_date is None
        and self.role == self.Role.MEMBER
    ):
        self.membership_date = date.today()

    # Automatically set membership expiry date
    if (
        self.role == self.Role.MEMBER
        and self.membership_date
        and self.membership_expiry_date is None
    ):
        self.membership_expiry_date = (
            self.membership_date + relativedelta(years=1)
        )

    super().save(*args, **kwargs)

    # Automatically generate membership code
    if (
        not self.membership_code
        and self.role == self.Role.MEMBER
    ):
        self.membership_code = (
            f"UGMWA-{self.membership_date.year}-{self.pk:06d}"
        )

        super().save(
            update_fields=["membership_code"]
        )