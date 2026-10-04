from rest_framework import viewsets
from accounts.permissions import IsPrincipalOrReadOnly
from .models import AcademicYear, SchoolClass, Section, Subject
from .serializers import (
    AcademicYearSerializer,
    SchoolClassSerializer,
    SectionSerializer,
    SubjectSerializer,
)


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all().order_by("-is_current", "-start_date")
    serializer_class = AcademicYearSerializer
    permission_classes = [IsPrincipalOrReadOnly]


class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all().order_by("display_order")
    serializer_class = SchoolClassSerializer
    permission_classes = [IsPrincipalOrReadOnly]


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related(
        "academic_year",
        "school_class",
    ).all().order_by("school_class__display_order", "name")
    serializer_class = SectionSerializer
    permission_classes = [IsPrincipalOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        class_id = self.request.query_params.get("class_id")
        if class_id:
            qs = qs.filter(school_class_id=class_id)
        return qs


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer
    permission_classes = [IsPrincipalOrReadOnly]