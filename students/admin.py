from django.contrib import admin

from .models import StudentProfile, StudentEnrollment


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "admission_number",
        "user",
        "gender",
        "status",
        "admission_date",
    )

    list_filter = (
        "gender",
        "status",
    )

    search_fields = (
        "admission_number",
        "user__username",
        "user__first_name",
        "user__last_name",
    )


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "academic_year",
        "school_class",
        "section",
        "roll_number",
        "is_current",
    )

    list_filter = (
        "academic_year",
        "school_class",
        "section",
        "is_current",
    )

    search_fields = (
        "student__admission_number",
        "student__user__first_name",
        "student__user__last_name",
    )

    ordering = (
        "academic_year",
        "school_class",
        "section",
        "roll_number",
    )