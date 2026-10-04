from decimal import Decimal

from rest_framework import serializers

from .models import FeeStructure, StudentFee, FeePayment


class FeeStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeeStructure

        fields = [
            "id",
            "academic_year",
            "name",
            "fee_type",
            "amount",
            "due_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class FeePaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeePayment

        fields = [
            "id",
            "student_fee",
            "amount",
            "payment_method",
            "transaction_reference",
            "payment_date",
            "remarks",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate(self, attrs):

        student_fee = attrs["student_fee"]
        payment_amount = attrs["amount"]

        if payment_amount <= 0:
            raise serializers.ValidationError(
                {"amount": "Payment amount must be greater than zero."}
            )

        already_paid = sum(
            payment.amount
            for payment in student_fee.payments.all()
        )

        remaining = student_fee.amount - already_paid

        if payment_amount > remaining:
            raise serializers.ValidationError(
                {
                    "amount": (
                        f"Payment exceeds remaining balance "
                        f"of ₹{remaining}."
                    )
                }
            )

        return attrs


class StudentFeeSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.user.get_full_name",
        read_only=True,
    )

    admission_number = serializers.CharField(
        source="student.admission_number",
        read_only=True,
    )

    fee_name = serializers.CharField(
        source="fee_structure.name",
        read_only=True,
    )

    total_paid = serializers.SerializerMethodField()

    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = StudentFee

        fields = [
            "id",
            "student",
            "student_name",
            "admission_number",
            "fee_structure",
            "fee_name",
            "amount",
            "total_paid",
            "remaining_amount",
            "status",
            "assigned_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student_name",
            "admission_number",
            "fee_name",
            "total_paid",
            "remaining_amount",
            "status",
            "assigned_at",
            "updated_at",
        ]

    def get_total_paid(self, obj):

        return sum(
            payment.amount
            for payment in obj.payments.all()
        )

    def get_remaining_amount(self, obj):

        total_paid = self.get_total_paid(obj)

        return max(
            Decimal("0.00"),
            obj.amount - total_paid,
        )