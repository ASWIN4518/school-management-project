from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    FeeStructureViewSet,
    StudentFeeViewSet,
    FeePaymentViewSet,
)

router = DefaultRouter()

router.register(
    "structures",
    FeeStructureViewSet,
    basename="fee-structure",
)

router.register(
    "student-fees",
    StudentFeeViewSet,
    basename="student-fee",
)

router.register(
    "payments",
    FeePaymentViewSet,
    basename="fee-payment",
)

urlpatterns = router.urls