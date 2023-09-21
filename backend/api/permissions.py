from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Кастомный пермишен для автора или только чтение.'''

    def has_object_permission(self, request, view, obj):
        '''Разрешить GET, HEAD, OPTIONS запросы всем.'''
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
