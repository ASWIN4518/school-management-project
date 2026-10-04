from django.conf import settings
from django.db import models

from academics.models import (
    AcademicYear,
    SchoolClass,
    Section,
    Subject,
)


class TeacherProfile(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        RESIGNED = "RESIGNED", "Resigned"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True,
    )

    date_of_birth = models.DateField()

    phone = models.CharField(
        max_length=15,
    )

    address = models.TextField(
        blank=True,
    )

    joining_date = models.DateField()

    designation = models.CharField(
        max_length=100,
        default="Teacher",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class TeacherAssignment(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.PROTECT,
        related_name="assignments",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )

    is_class_teacher = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "subject",
                    "school_class",
                    "section",
                    "academic_year",
                ],
                name="unique_teacher_subject_assignment",
            )
        ]

    def __str__(self):
        return (
            f"{self.teacher.user.get_full_name()} - "
            f"{self.subject.name} - "
            f"{self.school_class.name} "
            f"{self.section.name} - "
            f"{self.academic_year.name}"
        )