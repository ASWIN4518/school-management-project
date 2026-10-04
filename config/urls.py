from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),

    # Web Portal UI (Real-time Website)
    path("", include("portal.urls")),

    # REST APIs
    path("api/auth/token/", obtain_auth_token),
    path("api/accounts/", include("accounts.urls")),
    path("api/students/", include("students.urls")),
    path("api/teachers/", include("teachers.urls")),
    path("api/academics/", include("academics.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/leave/", include("leave_management.urls")),
    path("api/fees/", include("fees.urls")),
]