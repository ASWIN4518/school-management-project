from django.db import models

from academics.models import AcademicYear
from students.models import StudentProfile


class FeeStructure(models.Model):

    class FeeType(models.TextChoices):
        TUITION = "TUITION", "Tuition Fee"
        TRANSPORT = "TRANSPORT", "Transport Fee"
        SPORTS = "SPORTS", "Sports Fee"
        EXAM = "EXAM", "Exam Fee"
        LIBRARY = "LIBRARY", "Library Fee"
        OTHER = "OTHER", "Other Fee"

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="fee_structures",
    )

    name = models.CharField(max_length=100)

    fee_type = models.CharField(
        max_length=20,
        choices=FeeType.choices,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    due_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "name"],
                name="unique_fee_structure_per_year",
            )
        ]

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class StudentFee(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PARTIAL = "PARTIAL", "Partially Paid"
        PAID = "PAID", "Paid"
        WAIVED = "WAIVED", "Waived"

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.PROTECT,
        related_name="fees",
    )

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name="student_fees",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "fee_structure"],
                name="unique_student_fee",
            )
        ]

    def __str__(self):
        return f"{self.student.admission_number} - {self.fee_structure.name}"


class FeePayment(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    payment_date = models.DateField()

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.student_fee.student.admission_number} "
            f"- ₹{self.amount}"
        )