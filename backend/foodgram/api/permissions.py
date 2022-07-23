from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.user.is_authenticated and request.user.is_admin
                or request.method in permissions.SAFE_METHODS)


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
