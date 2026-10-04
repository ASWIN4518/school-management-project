from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import TeacherAssignment, TeacherProfile

User = get_user_model()


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(
        source="subject.name",
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
        model = TeacherAssignment
        fields = [
            "id",
            "subject",
            "subject_name",
            "school_class",
            "class_name",
            "section",
            "section_name",
            "academic_year",
            "academic_year_name",
            "is_class_teacher",
            "is_active",
        ]


class TeacherProfileSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    assignments = TeacherAssignmentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = TeacherProfile
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "teacher_name",
            "employee_id",
            "date_of_birth",
            "phone",
            "address",
            "joining_date",
            "designation",
            "status",
            "assignments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "teacher_name",
            "assignments",
            "created_at",
            "updated_at",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name", "")

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.Role.TEACHER,
        )

        return TeacherProfile.objects.create(
            user=user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)

        user = instance.user

        if username is not None and username != user.username:
            if User.objects.filter(username=username).exclude(
                pk=user.pk
            ).exists():
                raise serializers.ValidationError({
                    "username": "Username already exists."
                })
            user.username = username

        if first_name is not None:
            user.first_name = first_name

        if last_name is not None:
            user.last_name = last_name

        if password:
            user.set_password(password)

        user.save()

        return super().update(instance, validated_data)

    def get_teacher_name(self, obj):
        return obj.user.get_full_name()