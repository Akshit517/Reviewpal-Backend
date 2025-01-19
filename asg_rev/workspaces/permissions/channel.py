from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from workspaces.models import Channel

class RolePermissionMixin:
    def get_channel(self, view):
        channel_id = view.kwargs.get('channel_pk',view.kwargs.get('pk'))
        if not channel_id:
            return None
        try: 
            return Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            raise NotFound("Channel not found")

    def has_role_permission(self, request, view, role):
        if not request.user.is_authenticated:
            return False

        channel = self.get_channel(view)
        if not channel:
            return False

        return request.user.channel_role.filter(
            user=request.user,
            channel=channel, 
            role=role
        ).exists()

    def is_channel_member(self, request, view):
        channel_id = view.kwargs.get('channel_pk',view.kwargs.get('pk'))
        print("first with channel_id", channel_id)
        channel = Channel.objects.filter(id=channel_id)
        if not request.user.is_authenticated:
            return False

        channel = self.get_channel(view)
        if not channel:
            return False
        
        return request.user.channel_role.filter(
            user=request.user,
            channel=channel
        ).exists()

class IsReviewer(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        print("executing is reviewer permission", self.has_role_permission(request, view, 'reviewer'))
        return self.has_role_permission(request, view, 'reviewer')

class IsReviewee(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        print("executing is reviewees permission", self.has_role_permission(request, view, 'reviewee'))
        return self.has_role_permission(request, view, 'reviewee')

class IsChannelMember(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        print("executing is channel member permission",  self.has_role_permission(request, view, 'reviewee'))
        return self.is_channel_member(request, view)
