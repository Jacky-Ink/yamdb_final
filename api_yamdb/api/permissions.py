from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, obj):
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_admin
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (request.user.is_staff or request.user.is_admin)


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, obj):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_anonymous
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moder
        )
