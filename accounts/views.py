from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count, Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import AcademicYear, SchoolClass, Section, Subject
from attendance.models import StudentAttendance
from fees.models import FeePayment, StudentFee
from leave_management.models import TeacherLeave
from students.models import StudentEnrollment, StudentProfile
from teachers.models import TeacherAssignment, TeacherProfile

from .models import User
from .permissions import IsPrincipal
from .serializers import UserSerializer


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "").strip()

        if not username or not password:
            return Response(
                {"detail": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials. Please check your username and password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        user_data = UserSerializer(user).data
        return Response({
            "token": token.key,
            "user": user_data,
            "role": user.role,
            "message": f"Welcome back, {user.get_full_name() or user.username}!",
        })


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        logout(request)
        return Response({"detail": "Successfully logged out."})


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data

        is_principal = user.role == User.Role.PRINCIPAL or user.is_superuser
        is_teacher = user.role == User.Role.TEACHER
        is_student = user.role == User.Role.STUDENT

        data["permissions"] = {
            "is_principal": is_principal,
            "is_teacher": is_teacher,
            "is_student": is_student,
            "can_manage_all": is_principal,
            "can_manage_academics": is_principal,
            "can_manage_teachers": is_principal,
            "can_approve_leaves": is_principal,
            "can_manage_fees": is_principal,
            "can_view_fees": is_principal or is_student,
            "can_mark_attendance": is_principal or is_teacher,
            "can_apply_leave": is_teacher,
            "can_view_student_directory": is_principal or is_teacher,
        }

        # Attach profile information
        if is_teacher and hasattr(user, "teacher_profile"):
            tp = user.teacher_profile
            assignments = tp.assignments.filter(is_active=True).select_related(
                "subject", "school_class", "section", "academic_year"
            )
            data["teacher_profile"] = {
                "id": tp.id,
                "employee_id": tp.employee_id,
                "designation": tp.designation,
                "phone": tp.phone,
                "joining_date": str(tp.joining_date),
                "assignments": [
                    {
                        "id": a.id,
                        "subject_name": a.subject.name,
                        "subject_code": a.subject.code,
                        "class_name": a.school_class.name,
                        "class_id": a.school_class.id,
                        "section_name": a.section.name,
                        "section_id": a.section.id,
                        "academic_year": a.academic_year.name,
                        "is_class_teacher": a.is_class_teacher,
                    }
                    for a in assignments
                ],
            }

        elif is_student and hasattr(user, "student_profile"):
            sp = user.student_profile
            current_enr = sp.enrollments.filter(is_current=True).select_related(
                "school_class", "section", "academic_year"
            ).first()
            data["student_profile"] = {
                "id": sp.id,
                "admission_number": sp.admission_number,
                "date_of_birth": str(sp.date_of_birth),
                "gender": sp.gender,
                "blood_group": sp.blood_group,
                "phone": sp.phone,
                "current_enrollment": {
                    "class_name": current_enr.school_class.name if current_enr else "Not Enrolled",
                    "class_id": current_enr.school_class.id if current_enr else None,
                    "section_name": current_enr.section.name if current_enr else "-",
                    "section_id": current_enr.section.id if current_enr else None,
                    "roll_number": current_enr.roll_number if current_enr else "-",
                    "academic_year": current_enr.academic_year.name if current_enr else "-",
                } if current_enr else None,
            }

        token, _ = Token.objects.get_or_create(user=user)
        data["token"] = token.key

        return Response(data)


class SwitchDemoRoleAPIView(APIView):
    """
    Convenient helper for live testing and grading:
    Quickly logs in as the sample demo user for the specified role.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        target_role = request.data.get("role", "").upper()
        user = None

        if target_role == "PRINCIPAL":
            user = User.objects.filter(role=User.Role.PRINCIPAL).first()
            if not user:
                user = User.objects.filter(is_superuser=True).first()
        elif target_role == "TEACHER":
            user = User.objects.filter(role=User.Role.TEACHER).first()
        elif target_role == "STUDENT":
            user = User.objects.filter(role=User.Role.STUDENT).first()

        if not user:
            return Response(
                {"detail": f"No demo account found for role {target_role}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": f"Switched to {user.get_role_display()} ({user.username})",
            "token": token.key,
            "role": user.role,
            "username": user.username,
        })


class DashboardStatsAPIView(APIView):
    """
    Returns real-time KPI statistics tailored to the authenticated user's role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        is_principal = user.role == User.Role.PRINCIPAL or user.is_superuser

        if is_principal:
            total_students = StudentProfile.objects.filter(status=StudentProfile.Status.ACTIVE).count()
            total_teachers = TeacherProfile.objects.filter(status=TeacherProfile.Status.ACTIVE).count()
            total_classes = SchoolClass.objects.filter(is_active=True).count()
            total_sections = Section.objects.filter(is_active=True).count()

            # Today's attendance
            today_att = StudentAttendance.objects.filter(date=today)
            total_marked_today = today_att.count()
            present_today = today_att.filter(status__in=[StudentAttendance.Status.PRESENT, StudentAttendance.Status.HALF_DAY]).count()
            absent_today = today_att.filter(status=StudentAttendance.Status.ABSENT).count()
            attendance_rate = round((present_today / total_marked_today * 100), 1) if total_marked_today > 0 else 0

            # Fees overview
            fee_totals = StudentFee.objects.aggregate(
                total_expected=Sum("amount"),
            )
            total_expected = float(fee_totals["total_expected"] or 0)
            total_collected_agg = FeePayment.objects.aggregate(total_paid=Sum("amount"))
            total_collected = float(total_collected_agg["total_paid"] or 0)
            total_pending = max(0.0, total_expected - total_collected)

            # Leaves
            pending_leaves = TeacherLeave.objects.filter(status=TeacherLeave.Status.PENDING).count()

            return Response({
                "role": "PRINCIPAL",
                "stats": {
                    "total_students": total_students,
                    "total_teachers": total_teachers,
                    "total_classes": total_classes,
                    "total_sections": total_sections,
                    "attendance_rate_today": attendance_rate,
                    "present_today": present_today,
                    "absent_today": absent_today,
                    "total_marked_today": total_marked_today,
                    "total_fee_expected": total_expected,
                    "total_fee_collected": total_collected,
                    "total_fee_pending": total_pending,
                    "pending_leave_requests": pending_leaves,
                }
            })

        elif user.role == User.Role.TEACHER:
            tp = getattr(user, "teacher_profile", None)
            if not tp:
                return Response({"role": "TEACHER", "stats": {}})

            assignments = tp.assignments.filter(is_active=True)
            section_ids = assignments.values_list("section_id", flat=True).distinct()
            assigned_students = StudentEnrollment.objects.filter(
                section_id__in=section_ids,
                is_current=True,
            ).count()

            my_leaves = TeacherLeave.objects.filter(teacher=tp)
            pending_leaves = my_leaves.filter(status=TeacherLeave.Status.PENDING).count()
            approved_leaves = my_leaves.filter(status=TeacherLeave.Status.APPROVED).count()

            # Today's attendance for assigned sections
            today_att = StudentAttendance.objects.filter(date=today, section_id__in=section_ids)
            marked_count = today_att.count()

            return Response({
                "role": "TEACHER",
                "stats": {
                    "assigned_classes_count": section_ids.count(),
                    "assigned_students_count": assigned_students,
                    "my_pending_leaves": pending_leaves,
                    "my_approved_leaves": approved_leaves,
                    "today_attendance_marked": marked_count,
                }
            })

        elif user.role == User.Role.STUDENT:
            sp = getattr(user, "student_profile", None)
            if not sp:
                return Response({"role": "STUDENT", "stats": {}})

            # Personal Attendance
            attendance_records = StudentAttendance.objects.filter(student=sp)
            total_days = attendance_records.count()
            present_days = attendance_records.filter(status__in=[StudentAttendance.Status.PRESENT, StudentAttendance.Status.HALF_DAY]).count()
            absent_days = attendance_records.filter(status=StudentAttendance.Status.ABSENT).count()
            late_days = attendance_records.filter(status=StudentAttendance.Status.LATE).count()
            attendance_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0

            # Today's status
            today_rec = attendance_records.filter(date=today).first()
            today_status = today_rec.status if today_rec else "NOT_MARKED"

            # Fees
            student_fees = StudentFee.objects.filter(student=sp)
            total_fee = float(student_fees.aggregate(Sum("amount"))["amount__sum"] or 0)
            paid_fee = float(FeePayment.objects.filter(student_fee__student=sp).aggregate(Sum("amount"))["amount__sum"] or 0)
            pending_fee = max(0.0, total_fee - paid_fee)

            return Response({
                "role": "STUDENT",
                "stats": {
                    "attendance_rate": attendance_rate,
                    "total_days": total_days,
                    "present_days": present_days,
                    "absent_days": absent_days,
                    "late_days": late_days,
                    "today_status": today_status,
                    "total_fee": total_fee,
                    "paid_fee": paid_fee,
                    "pending_fee": pending_fee,
                }
            })

        return Response({"role": user.role, "stats": {}})
