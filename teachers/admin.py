from django.contrib import admin

from .models import TeacherProfile, TeacherAssignment


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "user",
        "designation",
        "status",
        "joining_date",
    )

    list_filter = (
        "status",
        "designation",
    )

    search_fields = (
        "employee_id",
        "user__username",
        "user__first_name",
        "user__last_name",
    )


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "subject",
        "school_class",
        "section",
        "academic_year",
        "is_class_teacher",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "school_class",
        "section",
        "subject",
        "is_class_teacher",
        "is_active",
    )

    search_fields = (
        "teacher__employee_id",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "subject__name",
        "subject__code",
    )

    ordering = (
        "academic_year",
        "school_class",
        "section",
        "subject",
    )