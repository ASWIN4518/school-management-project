from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    SchoolClassViewSet,
    SectionViewSet,
    SubjectViewSet,
)


router = DefaultRouter()

router.register(
    "academic-years",
    AcademicYearViewSet,
    basename="academic-year",
)

router.register(
    "classes",
    SchoolClassViewSet,
    basename="school-class",
)

router.register(
    "sections",
    SectionViewSet,
    basename="section",
)

router.register(
    "subjects",
    SubjectViewSet,
    basename="subject",
)


urlpatterns = [
    path("", include(router.urls)),
]