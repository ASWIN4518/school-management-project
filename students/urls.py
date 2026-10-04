from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    StudentDetailAPIView,
    StudentEnrollmentViewSet,
    StudentListCreateAPIView,
)


router = DefaultRouter()

router.register(
    "enrollments",
    StudentEnrollmentViewSet,
    basename="student-enrollment",
)


urlpatterns = [
    path("", StudentListCreateAPIView.as_view()),
    path("<int:pk>/", StudentDetailAPIView.as_view()),
    path("", include(router.urls)),
]