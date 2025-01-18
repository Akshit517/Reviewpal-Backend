from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from workspaces.models import (
    Submission,
    ChannelRole
)

class RolePermissionMixin:
    def get_submission(self, view):
        submission_id = view.kwargs.get('submission_pk',view.kwargs.get('pk'))
        if not submission_id:
            return None
        try: 
            return Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            raise NotFound("Submission not found")

    def get_team_members(self, request, submission: Submission):
        team_members = ChannelRole.objects.filter(
            channel=submission.assignment.id,
            team=submission.sender_team
        )
        return team_members

    def has_role_permission(self, request, view):
        submission = self.get_submission(view)
        team_members = self.get_team_members(request, submission)
        return team_members.filter(user=request.user).exists()

class IsTeamMember(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        print("executing is team member permission",  self.has_role_permission(request, view))
        return self.has_role_permission(request, view)