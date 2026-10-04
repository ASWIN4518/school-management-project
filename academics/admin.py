from django.contrib import admin
from .models import AcademicYear, SchoolClass, Section, Subject


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = ("is_current",)
    search_fields = ("name",)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_order",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("display_order",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school_class",
        "academic_year",
        "capacity",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "school_class",
        "is_active",
    )
    search_fields = (
        "name",
        "school_class__name",
        "academic_year__name",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = (
        "code",
        "name",
    )