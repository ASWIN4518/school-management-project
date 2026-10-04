from rest_framework import serializers

from .models import AcademicYear, SchoolClass, Section, Subject


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "is_current",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = [
            "id",
            "name",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SectionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(
        source="school_class.name",
        read_only=True,
    )
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )

    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "academic_year",
            "academic_year_name",
            "school_class",
            "class_name",
            "capacity",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "academic_year_name",
            "class_name",
            "created_at",
            "updated_at",
        ]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]