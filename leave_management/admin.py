from django.contrib import admin

from .models import TeacherLeave


@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "reviewer",
        "applied_at",
    )

    list_filter = (
        "leave_type",
        "status",
        "start_date",
        "end_date",
    )

    search_fields = (
        "teacher__employee_id",
        "teacher__user__first_name",
        "teacher__user__last_name",
    )

    ordering = (
        "-applied_at",
    )