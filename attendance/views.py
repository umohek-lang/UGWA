from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    AttendanceRecord,
    AttendanceSession,
)


@login_required
def attendance_list(request):

    sessions = AttendanceSession.objects.all()

    return render(
        request,
        "attendance/session_list.html",
        {
            "sessions": sessions
        }
    )


@login_required
def attendance_detail(request, pk):

    session = get_object_or_404(
        AttendanceSession,
        pk=pk
    )

    records = AttendanceRecord.objects.filter(
        session=session
    ).select_related(
        "member",
        "marked_by"
    )

    total_records = records.count()

    present_count = records.filter(
        status=AttendanceRecord.Status.PRESENT
    ).count()

    late_count = records.filter(
        status=AttendanceRecord.Status.LATE
    ).count()

    absent_count = records.filter(
        status=AttendanceRecord.Status.ABSENT
    ).count()

    excused_count = records.filter(
        status=AttendanceRecord.Status.EXCUSED
    ).count()

    context = {
        "session": session,
        "records": records,
        "total_records": total_records,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
        "excused_count": excused_count,
    }

    return render(
        request,
        "attendance/session_detail.html",
        context
    )


@login_required
def my_attendance(request):

    records = AttendanceRecord.objects.filter(
        member=request.user
    ).select_related(
        "session"
    )

    total = records.count()

    present = records.filter(
        status=AttendanceRecord.Status.PRESENT
    ).count()

    late = records.filter(
        status=AttendanceRecord.Status.LATE
    ).count()

    absent = records.filter(
        status=AttendanceRecord.Status.ABSENT
    ).count()

    excused = records.filter(
        status=AttendanceRecord.Status.EXCUSED
    ).count()

    attendance_rate = 0

    if total:
        attendance_rate = (
            (present + late) / total
        ) * 100

    context = {
        "records": records,
        "total": total,
        "present": present,
        "late": late,
        "absent": absent,
        "excused": excused,
        "attendance_rate": attendance_rate,
    }

    return render(
        request,
        "attendance/my_attendance.html",
        context
    )


@login_required
def mark_attendance(request, pk):

    session = get_object_or_404(
        AttendanceSession,
        pk=pk
    )

    if not (
        request.user.is_superuser
        or request.user.is_staff
    ):
        messages.error(
            request,
            "You do not have permission to manage attendance."
        )

        return redirect(
            "attendance:detail",
            pk=session.pk
        )

    if not session.is_open:

        messages.warning(
            request,
            "This attendance session is closed."
        )

        return redirect(
            "attendance:detail",
            pk=session.pk
        )

    User = request.user.__class__

    members = list(
        User.objects.filter(
            is_active=True
        ).order_by(
            "first_name",
            "last_name",
            "username"
        )
    )

    existing_records = {
        record.member_id: record
        for record in AttendanceRecord.objects.filter(
            session=session
        )
    }

    if request.method == "POST":

        with transaction.atomic():

            for member in members:

                status = request.POST.get(
                    f"status_{member.pk}",
                    AttendanceRecord.Status.ABSENT
                )

                remarks = request.POST.get(
                    f"remarks_{member.pk}",
                    ""
                ).strip()

                valid_statuses = {
                    choice[0]
                    for choice in AttendanceRecord.Status.choices
                }

                if status not in valid_statuses:
                    status = AttendanceRecord.Status.ABSENT

                record = existing_records.get(
                    member.pk
                )

                if record:

                    record.status = status
                    record.remarks = remarks
                    record.marked_by = request.user

                    record.save(
                        update_fields=[
                            "status",
                            "remarks",
                            "marked_by",
                            "updated_at",
                        ]
                    )

                else:

                    AttendanceRecord.objects.create(
                        session=session,
                        member=member,
                        status=status,
                        remarks=remarks,
                        marked_by=request.user,
                    )

        messages.success(
            request,
            "Attendance records have been saved successfully."
        )

        return redirect(
            "attendance:detail",
            pk=session.pk
        )

    member_rows = []

    for member in members:

        member_rows.append(
            {
                "member": member,
                "record": existing_records.get(
                    member.pk
                ),
            }
        )

    context = {
        "session": session,
        "member_rows": member_rows,
        "status_choices": AttendanceRecord.Status.choices,
    }

    return render(
        request,
        "attendance/mark_attendance.html",
        context
    )