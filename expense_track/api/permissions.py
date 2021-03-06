from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only object user or admin can CRUD.
    """

    def has_permission(self, request, view, **kwargs):
        if request.user.is_superuser:
            return True
        return request.user.username == view.kwargs.get('username')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Only object user or admin can CRUD.
    """

    def has_permission(self, request, view, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False
