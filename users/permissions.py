from rest_framework import permissions


class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to only allow admins and managers to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_manager


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        # Owner can edit their own profile
        return obj == request.user


class CanEditShipment(permissions.BasePermission):
    """
    Custom permission to check if user can edit shipments.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.can_edit