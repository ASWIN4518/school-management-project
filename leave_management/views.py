from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsPrincipal, IsTeacher
from .models import TeacherLeave
from .serializers import TeacherLeaveSerializer


class TeacherLeaveViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherLeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = TeacherLeave.objects.select_related(
            "teacher__user",
            "reviewer",
        ).all().order_by("-applied_at")

        if user.role == User.Role.PRINCIPAL or user.is_superuser:
            return qs
        elif user.role == User.Role.TEACHER:
            if hasattr(user, "teacher_profile"):
                return qs.filter(teacher=user.teacher_profile)
            return qs.none()
        else:
            return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.TEACHER and hasattr(user, "teacher_profile")):
            raise PermissionDenied("Only registered teachers can submit leave applications.")

        serializer.save(
            teacher=user.teacher_profile,
            status=TeacherLeave.Status.PENDING,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def approve(self, request, pk=None):
        user = request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has authorization to approve leave applications.")

        leave = self.get_object()
        if leave.status != TeacherLeave.Status.PENDING:
            return Response(
                {"detail": "Only pending leave requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = TeacherLeave.Status.APPROVED
        leave.reviewer = request.user
        leave.reviewed_at = timezone.now()
        leave.review_remarks = request.data.get("review_remarks", "Approved by Principal")
        leave.save()

        return Response(
            TeacherLeaveSerializer(leave).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def reject(self, request, pk=None):
        user = request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has authorization to reject leave applications.")

        leave = self.get_object()
        if leave.status != TeacherLeave.Status.PENDING:
            return Response(
                {"detail": "Only pending leave requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = TeacherLeave.Status.REJECTED
        leave.reviewer = request.user
        leave.reviewed_at = timezone.now()
        leave.review_remarks = request.data.get("review_remarks", "Rejected by Principal")
        leave.save()

        return Response(
            TeacherLeaveSerializer(leave).data,
            status=status.HTTP_200_OK,
        )