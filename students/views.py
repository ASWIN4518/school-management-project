from django.db.models import Q
from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import IsPrincipal, IsPrincipalOrReadOnly
from .models import StudentEnrollment, StudentProfile
from .serializers import StudentEnrollmentSerializer, StudentProfileSerializer


class StudentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentProfile.objects.select_related("user").prefetch_related(
            "enrollments__school_class",
            "enrollments__section",
            "enrollments__academic_year",
        )

        # Principal & Superuser: Full unrestricted access
        if user.role == User.Role.PRINCIPAL or user.is_superuser:
            pass
        elif user.role == User.Role.TEACHER:
            # Teacher can view students in their assigned sections
            if hasattr(user, "teacher_profile"):
                section_ids = user.teacher_profile.assignments.filter(
                    is_active=True
                ).values_list("section_id", flat=True)
                student_ids = StudentEnrollment.objects.filter(
                    section_id__in=section_ids,
                    is_current=True,
                ).values_list("student_id", flat=True)
                queryset = queryset.filter(id__in=student_ids)
            else:
                queryset = queryset.none()
        elif user.role == User.Role.STUDENT:
            # Student can only view their own profile
            queryset = queryset.filter(user=user)
        else:
            queryset = queryset.none()

        # Query filters
        class_id = self.request.query_params.get("class_id")
        section_id = self.request.query_params.get("section_id")
        search = self.request.query_params.get("search")

        if class_id:
            queryset = queryset.filter(enrollments__school_class_id=class_id, enrollments__is_current=True)
        if section_id:
            queryset = queryset.filter(enrollments__section_id=section_id, enrollments__is_current=True)
        if search:
            queryset = queryset.filter(
                Q(admission_number__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__username__icontains=search)
            )

        return queryset.distinct()

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has permission to admit and register new students.")
        serializer.save()


class StudentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentProfile.objects.select_related("user").prefetch_related(
            "enrollments__school_class",
            "enrollments__section",
            "enrollments__academic_year",
        )

        if user.role == User.Role.PRINCIPAL or user.is_superuser:
            return queryset
        elif user.role == User.Role.TEACHER:
            if hasattr(user, "teacher_profile"):
                section_ids = user.teacher_profile.assignments.filter(
                    is_active=True
                ).values_list("section_id", flat=True)
                student_ids = StudentEnrollment.objects.filter(
                    section_id__in=section_ids,
                    is_current=True,
                ).values_list("student_id", flat=True)
                return queryset.filter(id__in=student_ids)
            return queryset.none()
        elif user.role == User.Role.STUDENT:
            return queryset.filter(user=user)
        return queryset.none()

    def perform_update(self, serializer):
        user = self.request.user
        # Principal can update all fields; Student can only update basic info if allowed, or Principal only
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can modify student master records.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can delete student records.")
        instance.delete()


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentEnrollment.objects.select_related(
            "student__user",
            "academic_year",
            "school_class",
            "section",
        ).all()

        if user.role == User.Role.PRINCIPAL or user.is_superuser:
            pass
        elif user.role == User.Role.TEACHER:
            if hasattr(user, "teacher_profile"):
                section_ids = user.teacher_profile.assignments.filter(
                    is_active=True
                ).values_list("section_id", flat=True)
                queryset = queryset.filter(section_id__in=section_ids)
            else:
                queryset = queryset.none()
        elif user.role == User.Role.STUDENT:
            queryset = queryset.filter(student__user=user)
        else:
            queryset = queryset.none()

        section_id = self.request.query_params.get("section_id")
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has permission to enroll students in classes.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has permission to update student enrollments.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal has permission to delete student enrollments.")
        instance.delete()