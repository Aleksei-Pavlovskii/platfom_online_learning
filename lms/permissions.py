from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(BasePermission):
    message = 'Модератор может только просматривать и редактировать.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.groups.filter(name='Moderators').exists():
            return False
        return request.method not in ('POST', 'DELETE')


class IsOwner(BasePermission):
    message = 'Вы можете работать только со своими объектами.'

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class IsModeratorOrOwner(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        is_moderator = request.user.groups.filter(name='Moderators').exists()
        if is_moderator:
            return request.method in SAFE_METHODS or request.method in ('PUT', 'PATCH')
        return True

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name='Moderators').exists()
        if is_moderator:
            return request.method in SAFE_METHODS or request.method in ('PUT', 'PATCH')
        return obj.owner_id == request.user.id


class IsProfileOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
