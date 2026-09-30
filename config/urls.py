from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from payments.views import verify_membership

admin.site.site_header = "UGMWA Administration"
admin.site.site_title = "UGMWA Admin"
admin.site.index_title = "UGMWA Management System"
urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        include("association.urls")
    ),

    path(
        "accounts/",
        include("accounts.urls")
    ),

    path(
        "dashboard/",
        include("dashboard.urls")
    ),
    path(
        "dashboard/",
        include("members.urls")
    ),

    path(
    "leadership/",
    include("executives.urls")
),
path(
    "events/",
    include("events.urls")
),
path(
    "announcements/",
    include("announcements.urls")
),

path(
    "payments/",
    include("payments.urls")
),

path(
    "finance/",
    include("finance.urls")
),
path(
    "documents/",
    include("documents.urls")
),

path(
    "attendance/",
    include("attendance.urls")
),

path(
    "welfare/",
    include("welfare.urls")
),

path(
    "membership/verify/<str:membership_code>/",
    verify_membership,
    name="verify_membership",
),

]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )