from django.urls import path
from .views import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    SwitchDemoRoleAPIView,
    DashboardStatsAPIView,
)

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="accounts-login"),
    path("logout/", LogoutAPIView.as_view(), name="accounts-logout"),
    path("me/", MeAPIView.as_view(), name="accounts-me"),
    path("switch-demo/", SwitchDemoRoleAPIView.as_view(), name="accounts-switch-demo"),
    path("stats/", DashboardStatsAPIView.as_view(), name="accounts-stats"),
]
