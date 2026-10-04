from django.db import models

from students.models import StudentProfile
from academics.models import AcademicYear, SchoolClass, Section


class StudentAttendance(models.Model):

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        HALF_DAY = "HALF_DAY", "Half Day"

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="student_attendance",
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="student_attendance",
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="student_attendance",
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )

    remarks = models.CharField(
        max_length=255,
        blank=True,
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
                    "student",
                    "date",
                ],
                name="unique_student_attendance_per_day",
            )
        ]

    def __str__(self):
        return (
            f"{self.student.admission_number} - "
            f"{self.date} - "
            f"{self.status}"
        )