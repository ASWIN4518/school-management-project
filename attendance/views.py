from datetime import date
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from academics.models import AcademicYear, SchoolClass, Section
from students.models import StudentEnrollment, StudentProfile
from .models import StudentAttendance
from .serializers import StudentAttendanceSerializer


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = StudentAttendance.objects.select_related(
            "student__user",
            "academic_year",
            "school_class",
            "section",
        ).all().order_by("-date", "school_class__display_order", "student__admission_number")

        # RBAC Filtering
        if user.role == User.Role.PRINCIPAL or user.is_superuser:
            pass
        elif user.role == User.Role.TEACHER:
            if hasattr(user, "teacher_profile"):
                section_ids = user.teacher_profile.assignments.filter(
                    is_active=True
                ).values_list("section_id", flat=True)
                qs = qs.filter(section_id__in=section_ids)
            else:
                qs = qs.none()
        elif user.role == User.Role.STUDENT:
            qs = qs.filter(student__user=user)
        else:
            qs = qs.none()

        # Query Filters
        att_date = self.request.query_params.get("date")
        class_id = self.request.query_params.get("class_id")
        section_id = self.request.query_params.get("section_id")
        student_id = self.request.query_params.get("student_id")

        if att_date:
            qs = qs.filter(date=att_date)
        if class_id:
            qs = qs.filter(school_class_id=class_id)
        if section_id:
            qs = qs.filter(section_id=section_id)
        if student_id:
            qs = qs.filter(student_id=student_id)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            raise PermissionDenied("Students are not permitted to submit attendance records.")

        if user.role == User.Role.TEACHER:
            # Verify teacher is assigned to this section
            section = serializer.validated_data["section"]
            if not user.teacher_profile.assignments.filter(section=section, is_active=True).exists():
                raise PermissionDenied("You are not assigned to mark attendance for this section.")

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            raise PermissionDenied("Students cannot modify attendance records.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.role == User.Role.PRINCIPAL or user.is_superuser):
            raise PermissionDenied("Only the Principal can delete attendance records.")
        instance.delete()


class BulkAttendanceAPIView(APIView):
    """
    Real-time batch attendance marking for a class section.
    Allows a Teacher or Principal to mark the whole class at once.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        if user.role == User.Role.STUDENT:
            raise PermissionDenied("Students cannot mark attendance.")

        att_date = request.data.get("date") or str(date.today())
        academic_year_id = request.data.get("academic_year_id")
        school_class_id = request.data.get("school_class_id")
        section_id = request.data.get("section_id")
        records = request.data.get("records", [])

        if not all([academic_year_id, school_class_id, section_id, records]):
            return Response(
                {"detail": "date, academic_year_id, school_class_id, section_id, and records are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Teacher permission check
        if user.role == User.Role.TEACHER:
            has_assignment = user.teacher_profile.assignments.filter(
                section_id=section_id,
                is_active=True
            ).exists()
            if not has_assignment:
                raise PermissionDenied("You are not assigned to mark attendance for this class section.")

        academic_year = AcademicYear.objects.get(pk=academic_year_id)
        school_class = SchoolClass.objects.get(pk=school_class_id)
        section = Section.objects.get(pk=section_id)

        updated_count = 0
        created_count = 0

        for item in records:
            student_id = item.get("student_id")
            att_status = item.get("status", StudentAttendance.Status.PRESENT)
            remarks = item.get("remarks", "")

            student = StudentProfile.objects.get(pk=student_id)

            obj, created = StudentAttendance.objects.update_or_create(
                student=student,
                date=att_date,
                defaults={
                    "academic_year": academic_year,
                    "school_class": school_class,
                    "section": section,
                    "status": att_status,
                    "remarks": remarks,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            "message": f"Successfully recorded attendance for {len(records)} students on {att_date}.",
            "created": created_count,
            "updated": updated_count,
            "date": att_date,
        }, status=status.HTTP_200_OK)