from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Кастомный пермишен, запрещающий редактировать чужие записи."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
