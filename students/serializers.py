from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import StudentEnrollment, StudentProfile

User = get_user_model()


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    academic_year = serializers.CharField(source="academic_year.name")
    class_name = serializers.CharField(source="school_class.name")
    section = serializers.CharField(source="section.name")

    class Meta:
        model = StudentEnrollment
        fields = [
            "academic_year",
            "class_name",
            "section",
            "roll_number",
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    current_enrollment = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "admission_number",
            "student_name",
            "current_enrollment",
            "date_of_birth",
            "gender",
            "phone",
            "address",
            "blood_group",
            "admission_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_name",
            "current_enrollment",
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
            role=User.Role.STUDENT,
        )

        return StudentProfile.objects.create(
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

    def get_student_name(self, obj):
        return obj.user.get_full_name()

    def get_current_enrollment(self, obj):
        enrollment = obj.enrollments.filter(
            is_current=True
        ).first()

        if not enrollment:
            return None

        return StudentEnrollmentSerializer(enrollment).data
    
class StudentEnrollmentSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(
        source="academic_year.name",
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

    student_name = serializers.CharField(
        source="student.user.get_full_name",
        read_only=True,
    )

    class Meta:
        model = StudentEnrollment
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
            "roll_number",
            "is_current",
            "enrolled_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student_name",
            "academic_year_name",
            "class_name",
            "section_name",
            "enrolled_at",
            "updated_at",
        ]

    def validate(self, attrs):
        school_class = attrs["school_class"]
        section = attrs["section"]
        academic_year = attrs["academic_year"]

        if section.school_class_id != school_class.id:
            raise serializers.ValidationError({
                "section": "This section does not belong to the selected class."
            })

        if section.academic_year_id != academic_year.id:
            raise serializers.ValidationError({
                "section": "This section does not belong to the selected academic year."
            })

        return attrs