from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BulkAttendanceAPIView, StudentAttendanceViewSet

router = DefaultRouter()
router.register(
    "student-attendance",
    StudentAttendanceViewSet,
    basename="student-attendance",
)

urlpatterns = [
    path("bulk-mark/", BulkAttendanceAPIView.as_view(), name="attendance-bulk-mark"),
    path("", include(router.urls)),
]