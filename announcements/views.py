from django.shortcuts import get_object_or_404, render

from .models import Announcement


def announcement_list(request):

    announcements = Announcement.objects.filter(
        is_published=True
    )

    return render(
        request,
        "announcements/announcement_list.html",
        {
            "announcements": announcements,
        }
    )


def announcement_detail(request, slug):

    announcement = get_object_or_404(
        Announcement,
        slug=slug,
        is_published=True
    )

    return render(
        request,
        "announcements/announcement_detail.html",
        {
            "announcement": announcement,
        }
    )