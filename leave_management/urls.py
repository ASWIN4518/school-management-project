from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TeacherLeaveViewSet


router = DefaultRouter()

router.register(
    "teacher-leaves",
    TeacherLeaveViewSet,
    basename="teacher-leave",
)


urlpatterns = [
    path("", include(router.urls)),
]