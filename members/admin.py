from django.contrib import admin
from django.utils import timezone

from .models import MembershipCategory, MemberProfile


@admin.register(MembershipCategory)
class MembershipCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "annual_fee",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.action(description="Approve selected members")
def approve_members(modeladmin, request, queryset):

    for profile in queryset.select_related("user"):

        if not profile.membership_number:
            profile.membership_number = (
                f"ASS-{profile.pk:06d}"
            )

        profile.status = MemberProfile.Status.ACTIVE

        if not profile.joined_date:
            profile.joined_date = timezone.localdate()

        profile.approved_at = timezone.now()

        profile.save()

        profile.user.is_approved = True

        profile.user.save(
            update_fields=["is_approved"]
        )


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):

    list_display = (
        "membership_number",
        "get_full_name",
        "membership_category",
        "branch",
        "status",
        "user_approval",
        "joined_date",
    )

    list_filter = (
        "status",
        "membership_category",
        "branch",
    )

    search_fields = (
        "membership_number",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone",
    )

    actions = (
        approve_members,
    )

    readonly_fields = (
        "membership_number",
        "approved_at",
        "created_at",
        "updated_at",
    )

    def get_full_name(self, obj):

        return obj.user.get_full_name() or obj.user.username

    get_full_name.short_description = "Member"

    def user_approval(self, obj):

        if obj.user.is_approved:
            return "Approved"

        return "Pending"

    user_approval.short_description = "Account Status"