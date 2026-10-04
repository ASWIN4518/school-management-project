from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect("portal-dashboard")
    return render(request, "login.html")


@login_required(login_url="portal-login")
def dashboard_view(request):
    return render(request, "dashboard.html", {
        "user": request.user,
        "role": request.user.role,
        "is_principal": request.user.role == request.user.Role.PRINCIPAL or request.user.is_superuser,
        "is_teacher": request.user.role == request.user.Role.TEACHER,
        "is_student": request.user.role == request.user.Role.STUDENT,
    })


def logout_view(request):
    logout(request)
    return redirect("portal-login")
