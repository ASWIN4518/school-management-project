from django.contrib import admin

from .models import StudentAttendance


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "date",
        "status",
        "academic_year",
        "school_class",
        "section",
    )

    list_filter = (
        "date",
        "status",
        "academic_year",
        "school_class",
        "section",
    )

    search_fields = (
        "student__admission_number",
        "student__user__first_name",
        "student__user__last_name",
    )

    ordering = (
        "-date",
        "school_class",
        "section",
        "student",
    )