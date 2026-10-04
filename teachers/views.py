from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import IsPrincipal
from .models import TeacherAssignment, TeacherProfile
from .serializers import TeacherAssignmentSerializer, TeacherProfileSerializer


class TeacherListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeacherProfile.objects.select_related("user").prefetch_related(
            "assignments__subject",
            "assignments__school_class",
            "assignments__section",
            "assignments__academic_year",
        ).all()

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has permission to hire and register teachers.")
        serializer.save()


class TeacherDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherProfile.objects.select_related("user").prefetch_related(
        "assignments__subject",
        "assignments__school_class",
        "assignments__section",
        "assignments__academic_year",
    )
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        # Principal can update all; Teacher can update their own phone & address
        if user.role == User.Role.PRINCIPAL or user.is_superuser:
            serializer.save()
        elif user.role == User.Role.TEACHER and instance.user == user:
            # allow updating personal info
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to modify this teacher profile.")

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can delete teacher profiles.")
        instance.delete()


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = TeacherAssignment.objects.select_related(
            "teacher__user",
            "subject",
            "school_class",
            "section",
            "academic_year",
        ).filter(is_active=True)

        if user.role == User.Role.TEACHER and hasattr(user, "teacher_profile"):
            teacher_id = self.request.query_params.get("teacher_id")
            if teacher_id:
                return qs.filter(teacher_id=teacher_id)
            return qs.filter(teacher=user.teacher_profile)
        
        section_id = self.request.query_params.get("section_id")
        if section_id:
            qs = qs.filter(section_id=section_id)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can assign subjects and classes to teachers.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can alter teacher assignments.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can remove teacher assignments.")
        instance.delete()