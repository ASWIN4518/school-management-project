from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TeacherAssignmentViewSet,
    TeacherDetailAPIView,
    TeacherListCreateAPIView,
)

router = DefaultRouter()
router.register("assignments", TeacherAssignmentViewSet, basename="teacher-assignment")

urlpatterns = [
    path("", TeacherListCreateAPIView.as_view(), name="teacher-list-create"),
    path("<int:pk>/", TeacherDetailAPIView.as_view(), name="teacher-detail"),
    path("", include(router.urls)),
]