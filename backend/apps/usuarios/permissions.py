from rest_framework import permissions


class SoloAdmin(permissions.BasePermission):
    """Permite solo a administradores."""
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'es_admin', False))


class EsAdminOGerente(permissions.BasePermission):
    """Permite a administradores o gerentes."""
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (getattr(user, 'es_admin', False) or getattr(user, 'es_gerente', False)))


class EsPropietarioOAdmin(permissions.BasePermission):
    """Permite al propietario del objeto o a un administrador."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(user and user.is_authenticated and (obj == user or getattr(user, 'es_admin', False)))


