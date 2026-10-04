import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from academics.models import AcademicYear, SchoolClass, Section, Subject
from students.models import StudentProfile, StudentEnrollment
from teachers.models import TeacherProfile, TeacherAssignment
from attendance.models import StudentAttendance
from fees.models import FeeStructure, StudentFee, FeePayment
from leave_management.models import TeacherLeave


class Command(BaseCommand):
    help = "Seed realistic production-style demo data with Principal, Teachers, and Students"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        # 1. Academic Year
        ay = AcademicYear.objects.filter(is_current=True).first()
        if not ay:
            ay, _ = AcademicYear.objects.get_or_create(
                name="2026-2027",
                defaults={
                    "start_date": datetime.date(2026, 6, 1),
                    "end_date": datetime.date(2027, 4, 30),
                    "is_current": True,
                },
            )
            AcademicYear.objects.filter(id=ay.id).update(is_current=True)

        # 2. Classes (use existing or create)
        c10 = SchoolClass.objects.filter(display_order=10).first()
        if not c10:
            c10 = SchoolClass.objects.create(name="Class 10", display_order=10, is_active=True)
        else:
            c10.name = "Class 10"
            c10.save(update_fields=["name"])

        c9 = SchoolClass.objects.filter(display_order=9).first()
        if not c9:
            c9 = SchoolClass.objects.create(name="Class 9", display_order=9, is_active=True)

        c8 = SchoolClass.objects.filter(display_order=8).first()
        if not c8:
            c8 = SchoolClass.objects.create(name="Class 8", display_order=8, is_active=True)

        # 3. Sections
        sec10a = Section.objects.filter(academic_year=ay, school_class=c10, name="A").first()
        if not sec10a:
            sec10a = Section.objects.create(academic_year=ay, school_class=c10, name="A", capacity=40, is_active=True)

        sec10b = Section.objects.filter(academic_year=ay, school_class=c10, name="B").first()
        if not sec10b:
            sec10b = Section.objects.create(academic_year=ay, school_class=c10, name="B", capacity=40, is_active=True)

        sec9a = Section.objects.filter(academic_year=ay, school_class=c9, name="A").first()
        if not sec9a:
            sec9a = Section.objects.create(academic_year=ay, school_class=c9, name="A", capacity=40, is_active=True)

        # 4. Subjects
        sub_math = Subject.objects.filter(code__in=["MATH", "MATH101"]).first()
        if not sub_math:
            sub_math = Subject.objects.create(code="MATH101", name="Mathematics", description="Core Mathematics")

        sub_sci = Subject.objects.filter(code__in=["SCI", "PHY101"]).first()
        if not sub_sci:
            sub_sci = Subject.objects.create(code="SCI101", name="Science", description="Physics & Chemistry")

        sub_eng = Subject.objects.filter(code__in=["ENG", "ENG101"]).first()
        if not sub_eng:
            sub_eng = Subject.objects.create(code="ENG101", name="English", description="English Literature")

        sub_cs = Subject.objects.filter(code__in=["CS", "CS101"]).first()
        if not sub_cs:
            sub_cs = Subject.objects.create(code="CS101", name="Computer Science", description="Computer Fundamentals")

        # 5. Principal User (Full Access)
        principal_user = User.objects.filter(username="principal").first()
        if not principal_user:
            principal_user = User.objects.create_user(
                username="principal",
                password="password123",
                first_name="Dr. Rajiv",
                last_name="Verma",
                email="principal@school.edu",
                role=User.Role.PRINCIPAL,
            )
        else:
            principal_user.set_password("password123")
            principal_user.first_name = "Dr. Rajiv"
            principal_user.last_name = "Verma"
            principal_user.role = User.Role.PRINCIPAL
        principal_user.is_staff = True
        principal_user.is_superuser = True
        principal_user.save()

        # Update existing Aswin to Principal too
        User.objects.filter(username="Aswin").update(role=User.Role.PRINCIPAL)

        # 6. Teachers
        t1_user = User.objects.filter(username="teacher.rajesh").first()
        if not t1_user:
            t1_user = User.objects.create_user(
                username="teacher.rajesh",
                password="password123",
                first_name="Rajesh",
                last_name="Kumar",
                email="rajesh.kumar@school.edu",
                role=User.Role.TEACHER,
            )
        else:
            t1_user.set_password("password123")
            t1_user.role = User.Role.TEACHER
            t1_user.save()

        t1_profile, _ = TeacherProfile.objects.update_or_create(
            user=t1_user,
            defaults={
                "employee_id": "TCH-2024-001",
                "date_of_birth": datetime.date(1985, 4, 12),
                "phone": "+91 9876543210",
                "address": "42 Civil Lines, North Avenue, City",
                "joining_date": datetime.date(2020, 6, 15),
                "designation": "Senior PGT Mathematics",
                "status": TeacherProfile.Status.ACTIVE,
            },
        )

        t2_user = User.objects.filter(username="teacher.priya").first()
        if not t2_user:
            t2_user = User.objects.create_user(
                username="teacher.priya",
                password="password123",
                first_name="Priya",
                last_name="Sharma",
                email="priya.sharma@school.edu",
                role=User.Role.TEACHER,
            )
        else:
            t2_user.set_password("password123")
            t2_user.role = User.Role.TEACHER
            t2_user.save()

        t2_profile, _ = TeacherProfile.objects.update_or_create(
            user=t2_user,
            defaults={
                "employee_id": "TCH-2024-002",
                "date_of_birth": datetime.date(1990, 8, 24),
                "phone": "+91 9876543211",
                "address": "18 Model Town, Lake Road, City",
                "joining_date": datetime.date(2021, 7, 10),
                "designation": "PGT English & Computer Science",
                "status": TeacherProfile.Status.ACTIVE,
            },
        )

        # 7. Teacher Assignments
        # Rajesh Kumar -> Class 10-A Math (Class Teacher), Class 10-A Science, Class 10-B Math
        TeacherAssignment.objects.update_or_create(
            teacher=t1_profile, subject=sub_math, school_class=c10, section=sec10a, academic_year=ay,
            defaults={"is_class_teacher": True, "is_active": True}
        )
        TeacherAssignment.objects.update_or_create(
            teacher=t1_profile, subject=sub_sci, school_class=c10, section=sec10a, academic_year=ay,
            defaults={"is_class_teacher": False, "is_active": True}
        )
        TeacherAssignment.objects.update_or_create(
            teacher=t1_profile, subject=sub_math, school_class=c10, section=sec10b, academic_year=ay,
            defaults={"is_class_teacher": False, "is_active": True}
        )

        # Priya Sharma -> Class 10-A English, Class 9-A English (Class Teacher), Class 9-A CS
        TeacherAssignment.objects.update_or_create(
            teacher=t2_profile, subject=sub_eng, school_class=c10, section=sec10a, academic_year=ay,
            defaults={"is_class_teacher": False, "is_active": True}
        )
        TeacherAssignment.objects.update_or_create(
            teacher=t2_profile, subject=sub_eng, school_class=c9, section=sec9a, academic_year=ay,
            defaults={"is_class_teacher": True, "is_active": True}
        )
        TeacherAssignment.objects.update_or_create(
            teacher=t2_profile, subject=sub_cs, school_class=c9, section=sec9a, academic_year=ay,
            defaults={"is_class_teacher": False, "is_active": True}
        )

        # 8. Students
        s1_user = User.objects.filter(username="student.rahul").first()
        if not s1_user:
            s1_user = User.objects.create_user(
                username="student.rahul",
                password="password123",
                first_name="Rahul",
                last_name="Verma",
                email="rahul.verma@student.school.edu",
                role=User.Role.STUDENT,
            )
        else:
            s1_user.set_password("password123")
            s1_user.role = User.Role.STUDENT
            s1_user.save()

        s1_profile, _ = StudentProfile.objects.update_or_create(
            user=s1_user,
            defaults={
                "admission_number": "ADM-2026-001",
                "date_of_birth": datetime.date(2009, 8, 15),
                "gender": StudentProfile.Gender.MALE,
                "phone": "+91 9811223344",
                "address": "12 Lotus Apartments, Central Avenue",
                "blood_group": "B+",
                "admission_date": datetime.date(2023, 4, 1),
                "status": StudentProfile.Status.ACTIVE,
            },
        )

        StudentEnrollment.objects.update_or_create(
            student=s1_profile,
            academic_year=ay,
            defaults={
                "school_class": c10,
                "section": sec10a,
                "roll_number": 1,
                "is_current": True,
            },
        )

        s2_user = User.objects.filter(username="student.ananya").first()
        if not s2_user:
            s2_user = User.objects.create_user(
                username="student.ananya",
                password="password123",
                first_name="Ananya",
                last_name="Sen",
                email="ananya.sen@student.school.edu",
                role=User.Role.STUDENT,
            )
        else:
            s2_user.set_password("password123")
            s2_user.role = User.Role.STUDENT
            s2_user.save()

        s2_profile, _ = StudentProfile.objects.update_or_create(
            user=s2_user,
            defaults={
                "admission_number": "ADM-2026-002",
                "date_of_birth": datetime.date(2009, 11, 20),
                "gender": StudentProfile.Gender.FEMALE,
                "phone": "+91 9811223355",
                "address": "45 Green Park, Main Boulevard",
                "blood_group": "O+",
                "admission_date": datetime.date(2023, 4, 1),
                "status": StudentProfile.Status.ACTIVE,
            },
        )

        StudentEnrollment.objects.update_or_create(
            student=s2_profile,
            academic_year=ay,
            defaults={
                "school_class": c10,
                "section": sec10a,
                "roll_number": 2,
                "is_current": True,
            },
        )

        s3_user = User.objects.filter(username="student.arjun").first()
        if not s3_user:
            s3_user = User.objects.create_user(
                username="student.arjun",
                password="password123",
                first_name="Arjun",
                last_name="Singh",
                email="arjun.singh@student.school.edu",
                role=User.Role.STUDENT,
            )
        else:
            s3_user.set_password("password123")
            s3_user.role = User.Role.STUDENT
            s3_user.save()

        s3_profile, _ = StudentProfile.objects.update_or_create(
            user=s3_user,
            defaults={
                "admission_number": "ADM-2026-003",
                "date_of_birth": datetime.date(2010, 3, 14),
                "gender": StudentProfile.Gender.MALE,
                "phone": "+91 9811223366",
                "address": "77 Sunshine Towers, Sector 14",
                "blood_group": "A+",
                "admission_date": datetime.date(2024, 4, 1),
                "status": StudentProfile.Status.ACTIVE,
            },
        )

        StudentEnrollment.objects.update_or_create(
            student=s3_profile,
            academic_year=ay,
            defaults={
                "school_class": c9,
                "section": sec9a,
                "roll_number": 1,
                "is_current": True,
            },
        )

        # 9. Attendance History (Past 5 days + Today)
        today = datetime.date.today()
        dates = [today - datetime.timedelta(days=i) for i in range(5, -1, -1)]

        for d in dates:
            r_status = StudentAttendance.Status.LATE if d == dates[2] else StudentAttendance.Status.PRESENT
            StudentAttendance.objects.update_or_create(
                student=s1_profile,
                date=d,
                defaults={
                    "academic_year": ay,
                    "school_class": c10,
                    "section": sec10a,
                    "status": r_status,
                    "remarks": "On time" if r_status == StudentAttendance.Status.PRESENT else "Bus delay",
                },
            )

            StudentAttendance.objects.update_or_create(
                student=s2_profile,
                date=d,
                defaults={
                    "academic_year": ay,
                    "school_class": c10,
                    "section": sec10a,
                    "status": StudentAttendance.Status.PRESENT,
                    "remarks": "Regular",
                },
            )

            a_status = StudentAttendance.Status.ABSENT if d == dates[1] else StudentAttendance.Status.PRESENT
            StudentAttendance.objects.update_or_create(
                student=s3_profile,
                date=d,
                defaults={
                    "academic_year": ay,
                    "school_class": c9,
                    "section": sec9a,
                    "status": a_status,
                    "remarks": "Medical reason" if a_status == StudentAttendance.Status.ABSENT else "Present",
                },
            )

        # 10. Fee Structures
        f_tuition, _ = FeeStructure.objects.update_or_create(
            academic_year=ay,
            name="Annual Tuition Fee 2026-27",
            defaults={
                "fee_type": FeeStructure.FeeType.TUITION,
                "amount": Decimal("25000.00"),
                "due_date": datetime.date(2026, 11, 15),
                "is_active": True,
            },
        )

        f_transport, _ = FeeStructure.objects.update_or_create(
            academic_year=ay,
            name="School Bus Transport Fee - Term 1",
            defaults={
                "fee_type": FeeStructure.FeeType.TRANSPORT,
                "amount": Decimal("6000.00"),
                "due_date": datetime.date(2026, 10, 30),
                "is_active": True,
            },
        )

        f_exam, _ = FeeStructure.objects.update_or_create(
            academic_year=ay,
            name="Mid-Term Examination Fee",
            defaults={
                "fee_type": FeeStructure.FeeType.EXAM,
                "amount": Decimal("2500.00"),
                "due_date": datetime.date(2026, 12, 1),
                "is_active": True,
            },
        )

        # 11. Student Fees & Payments
        sf1, _ = StudentFee.objects.update_or_create(
            student=s1_profile,
            fee_structure=f_tuition,
            defaults={"amount": Decimal("25000.00"), "status": StudentFee.Status.PAID},
        )
        if not FeePayment.objects.filter(student_fee=sf1).exists():
            FeePayment.objects.create(
                student_fee=sf1,
                amount=Decimal("25000.00"),
                payment_date=datetime.date(2026, 8, 10),
                payment_method=FeePayment.PaymentMethod.UPI,
                transaction_reference="UPI/2026/89482910",
                remarks="Annual Tuition Paid via Google Pay",
            )

        sf2, _ = StudentFee.objects.update_or_create(
            student=s1_profile,
            fee_structure=f_transport,
            defaults={"amount": Decimal("6000.00"), "status": StudentFee.Status.PARTIAL},
        )
        if not FeePayment.objects.filter(student_fee=sf2).exists():
            FeePayment.objects.create(
                student_fee=sf2,
                amount=Decimal("3000.00"),
                payment_date=datetime.date(2026, 9, 5),
                payment_method=FeePayment.PaymentMethod.CARD,
                transaction_reference="CARD/TXN/55129",
                remarks="First installment paid",
            )

        sf3, _ = StudentFee.objects.update_or_create(
            student=s1_profile,
            fee_structure=f_exam,
            defaults={"amount": Decimal("2500.00"), "status": StudentFee.Status.PENDING},
        )

        sf4, _ = StudentFee.objects.update_or_create(
            student=s2_profile,
            fee_structure=f_tuition,
            defaults={"amount": Decimal("25000.00"), "status": StudentFee.Status.PAID},
        )
        if not FeePayment.objects.filter(student_fee=sf4).exists():
            FeePayment.objects.create(
                student_fee=sf4,
                amount=Decimal("25000.00"),
                payment_date=datetime.date(2026, 7, 20),
                payment_method=FeePayment.PaymentMethod.BANK_TRANSFER,
                transaction_reference="NEFT/SBIN/4910283",
                remarks="Net banking online payment",
            )

        # 12. Teacher Leaves
        TeacherLeave.objects.update_or_create(
            teacher=t1_profile,
            leave_type=TeacherLeave.LeaveType.CASUAL,
            start_date=today - datetime.timedelta(days=10),
            end_date=today - datetime.timedelta(days=9),
            defaults={
                "reason": "Family function and travel to home town.",
                "status": TeacherLeave.Status.APPROVED,
                "reviewer": principal_user,
                "reviewed_at": timezone.now() - datetime.timedelta(days=11),
                "review_remarks": "Approved. Class substitute arranged.",
            },
        )

        TeacherLeave.objects.update_or_create(
            teacher=t2_profile,
            leave_type=TeacherLeave.LeaveType.SICK,
            start_date=today + datetime.timedelta(days=1),
            end_date=today + datetime.timedelta(days=1),
            defaults={
                "reason": "Severe viral fever and physician consultation.",
                "status": TeacherLeave.Status.PENDING,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data successfully populated!"))
        self.stdout.write("Credentials:")
        self.stdout.write("  Principal : username 'principal'       | password 'password123'")
        self.stdout.write("  Teacher   : username 'teacher.rajesh'  | password 'password123'")
        self.stdout.write("  Student   : username 'student.rahul'   | password 'password123'")
