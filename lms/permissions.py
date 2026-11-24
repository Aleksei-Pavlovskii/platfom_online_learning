from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModeratorOrReadOnly(BasePermission):
    message = 'Модератор может только просматривать и редактировать.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        is_admin = request.user.is_staff
        is_moderator = request.user.groups.filter(name='Moderators').exists()

        if is_admin:
            return True

        if request.method in SAFE_METHODS:
            return True

        if is_moderator:
            return request.method in ('PUT', 'PATCH')

        return False
