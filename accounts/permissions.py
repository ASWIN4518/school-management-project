from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPrincipal(BasePermission):
    """
    Principal has complete, unrestricted access across the entire school management system.
    Superusers also inherit Principal privileges.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role == request.user.Role.PRINCIPAL
                or request.user.is_superuser
            )
        )


class IsTeacher(BasePermission):
    """
    Teacher has permissions restricted to their assigned classes, students, and attendance.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.TEACHER
        )


class IsStudent(BasePermission):
    """
    Student has strictly read-only or self-service access to their own data.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.STUDENT
        )


class IsOffice(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role == request.user.Role.OFFICE
                or request.user.role == request.user.Role.PRINCIPAL
                or request.user.is_superuser
            )
        )


class IsPTSir(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.PT_SIR
        )


class IsPrincipalOrReadOnly(BasePermission):
    """
    Principal can write; all other authenticated users (Teacher, Student) have read-only access.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user.role == request.user.Role.PRINCIPAL
            or request.user.is_superuser
        )


class IsPrincipalOrTeacher(BasePermission):
    """
    Allows access to Principals (full) and Teachers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in [request.user.Role.PRINCIPAL, request.user.Role.TEACHER]
                or request.user.is_superuser
            )
        )