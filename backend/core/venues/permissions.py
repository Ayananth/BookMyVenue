from rest_framework import permissions

from accounts.models import UserRole


class IsVenueOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role == UserRole.ADMIN:
            return True
        return obj.owner_id == user.id


class CanManageVenues(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in (
            UserRole.VENUE,
            UserRole.ADMIN,
        )
