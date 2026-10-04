from django.db import models

from teachers.models import TeacherProfile


class TeacherLeave(models.Model):

    class LeaveType(models.TextChoices):
        CASUAL = "CASUAL", "Casual Leave"
        SICK = "SICK", "Sick Leave"
        EARNED = "EARNED", "Earned Leave"
        EMERGENCY = "EMERGENCY", "Emergency Leave"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.PROTECT,
        related_name="leave_requests",
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
    )

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    applied_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reviewer = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_teacher_leaves",
    )

    review_remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.teacher.employee_id} - "
            f"{self.leave_type} - "
            f"{self.start_date} to {self.end_date}"
        )