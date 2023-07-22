from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомный пермишшен для автора или только чтение."""

    def has_object_permission(self, request, view, obj):
        # Разрешить GET, HEAD, OPTIONS запросы всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить PUT, PATCH, DELETE запросы только автору рецепта
        return obj.author == request.user
