from django.utils import timezone
from rest_framework import serializers

from .models import TeacherLeave


class TeacherLeaveSerializer(serializers.ModelSerializer):

    teacher_name = serializers.CharField(
        source="teacher.user.get_full_name",
        read_only=True,
    )

    employee_id = serializers.CharField(
        source="teacher.employee_id",
        read_only=True,
    )

    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name",
        read_only=True,
    )

    class Meta:
        model = TeacherLeave
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "employee_id",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "applied_at",
            "reviewed_at",
            "reviewer",
            "reviewer_name",
            "review_remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "teacher_name",
            "employee_id",
            "status",
            "applied_at",
            "reviewed_at",
            "reviewer",
            "reviewer_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_date = attrs["start_date"]
        end_date = attrs["end_date"]

        if end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        return attrs

    def create(self, validated_data):
        return TeacherLeave.objects.create(
            status=TeacherLeave.Status.PENDING,
            **validated_data,
        )