from django.conf import settings
from django.db import models

from academics.models import AcademicYear, SchoolClass, Section


class StudentProfile(models.Model):

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        TRANSFERRED = "TRANSFERRED", "Transferred"
        GRADUATED = "GRADUATED", "Graduated"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    admission_number = models.CharField(
        max_length=30,
        unique=True,
    )

    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    admission_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name()}"


class StudentEnrollment(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
    )

    roll_number = models.PositiveIntegerField()

    is_current = models.BooleanField(default=True)

    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "academic_year",
                ],
                name="unique_student_enrollment_per_year",
            ),
            models.UniqueConstraint(
                fields=[
                    "academic_year",
                    "school_class",
                    "section",
                    "roll_number",
                ],
                name="unique_roll_number_per_section_year",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.admission_number} - "
            f"{self.school_class.name} - "
            f"{self.section.name} - "
            f"{self.academic_year.name}"
        )