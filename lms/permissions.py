from rest_framework import permissions

class IsModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(name='moderators').exists()


class IsModeratorOrOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method == 'POST':
            if request.user.groups.filter(name='moderators').exists():
                return False

            return True

        return True
    
    def has_object_permission(self, request, view, obj):
        
        is_moderator = request.user.groups.filter(name='moderators').exists()

        if is_moderator:
            if request.method == 'DELETE':
                return False
            return True
        
        return obj.owner == request.user