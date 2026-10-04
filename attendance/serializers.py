from rest_framework import serializers

from .models import StudentAttendance


class StudentAttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.user.get_full_name",
        read_only=True,
    )

    class_name = serializers.CharField(
        source="school_class.name",
        read_only=True,
    )

    section_name = serializers.CharField(
        source="section.name",
        read_only=True,
    )

    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )

    class Meta:
        model = StudentAttendance
        fields = [
            "id",
            "student",
            "student_name",
            "academic_year",
            "academic_year_name",
            "school_class",
            "class_name",
            "section",
            "section_name",
            "date",
            "status",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student_name",
            "academic_year_name",
            "class_name",
            "section_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        student = attrs["student"]
        academic_year = attrs["academic_year"]
        school_class = attrs["school_class"]
        section = attrs["section"]

        enrollment = student.enrollments.filter(
            academic_year=academic_year,
            school_class=school_class,
            section=section,
            is_current=True,
        ).exists()

        if not enrollment:
            raise serializers.ValidationError(
                "Student is not currently enrolled in this class, section and academic year."
            )

        return attrs