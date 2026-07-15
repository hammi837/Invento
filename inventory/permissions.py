from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Only Admin role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsManagerOrAdmin(BasePermission):
    """Manager or Admin role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'manager')
        )


class IsAnyRole(BasePermission):
    """Any authenticated user (admin, manager, staff)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class ReadOnlyOrManagerAbove(BasePermission):
    """
    Staff: read-only (GET, HEAD, OPTIONS).
    Manager / Admin: full access.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return request.user.role in ('admin', 'manager', 'staff')
        return request.user.role in ('admin', 'manager')
