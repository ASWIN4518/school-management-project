from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from .models import FeePayment, FeeStructure, StudentFee
from .serializers import (
    FeePaymentSerializer,
    FeeStructureSerializer,
    StudentFeeSerializer,
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser:
            return FeeStructure.objects.select_related("academic_year").all()
        elif user.role == User.Role.STUDENT:
            return FeeStructure.objects.select_related("academic_year").filter(is_active=True)
        else:
            # Teacher has no access to fee structures
            raise PermissionDenied("Teachers are not authorized to view or configure school fee structures.")

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser):
            raise PermissionDenied("Only Principal or Office staff can create fee structures.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser):
            raise PermissionDenied("Only Principal or Office staff can update fee structures.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can delete fee structures.")
        instance.delete()


class StudentFeeViewSet(viewsets.ModelViewSet):
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = StudentFee.objects.select_related(
            "student__user",
            "fee_structure",
        ).prefetch_related("payments").all()

        if user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser:
            student_id = self.request.query_params.get("student_id")
            if student_id:
                qs = qs.filter(student_id=student_id)
            status_param = self.request.query_params.get("status")
            if status_param:
                qs = qs.filter(status=status_param)
            return qs
        elif user.role == User.Role.STUDENT:
            return qs.filter(student__user=user)
        else:
            raise PermissionDenied("Teachers do not have permission to view or manage fee ledger records.")

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser):
            raise PermissionDenied("Only Principal or Office staff can assign student fees.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser):
            raise PermissionDenied("Only Principal or Office staff can modify student fees.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can delete student fee allocations.")
        instance.delete()


class FeePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = FeePayment.objects.select_related(
            "student_fee__student__user",
            "student_fee__fee_structure",
        ).all().order_by("-payment_date")

        if user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser:
            student_fee_id = self.request.query_params.get("student_fee_id")
            if student_fee_id:
                qs = qs.filter(student_fee_id=student_fee_id)
            return qs
        elif user.role == User.Role.STUDENT:
            return qs.filter(student_fee__student__user=user)
        else:
            raise PermissionDenied("Teachers do not have permission to access financial fee transactions.")

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role in [User.Role.PRINCIPAL, User.Role.OFFICE] or user.is_superuser):
            raise PermissionDenied("Only Principal or Office staff can record fee payments.")

        payment = serializer.save()
        student_fee = payment.student_fee

        total_paid = sum(p.amount for p in student_fee.payments.all())

        if total_paid >= student_fee.amount:
            student_fee.status = StudentFee.Status.PAID
        elif total_paid > 0:
            student_fee.status = StudentFee.Status.PARTIAL
        else:
            student_fee.status = StudentFee.Status.PENDING

        student_fee.save(update_fields=["status", "updated_at"])