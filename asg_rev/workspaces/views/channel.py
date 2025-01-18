from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import User
from workspaces import utils
from workspaces.models import (
    Category,
    Channel, 
    ChannelRole,
    Assignment,
    Team
)
from workspaces.serializers import (
    ChannelSerializer, 
    AssignmentSerializer,
    ChannelRoleSerializer
)
from workspaces.permissions import (
    IsReviewer, 
    IsReviewee, 
    IsCategoryMember,
    IsChannelMember,
    IsWorkspaceOwnerOrAdmin,
    IsWorkspaceMember,
)

class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer

    def get_queryset(self):
        user = self.request.user
        category_id = self.kwargs.get('category_pk')
        channel_ids = ChannelRole.objects.filter(user=user).values_list('channel', flat=True)
        return Channel.objects.filter(
            id__in=channel_ids,
            category_id=category_id
        )

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            permission_classes = [IsWorkspaceOwnerOrAdmin | IsReviewer]
        elif self.action in ['list']:
            permission_classes = [ IsWorkspaceOwnerOrAdmin | IsCategoryMember ]
        elif  self.action in ['retrieve']:
            permission_classes = [ IsWorkspaceOwnerOrAdmin | IsChannelMember ]

        return [permission() for permission in permission_classes]

class ChannelMemberView(APIView):
    def get_permissions(self):
        if self.request.method in ['POST','DELETE','PUT']:
            permission_classes = [IsWorkspaceOwnerOrAdmin | IsReviewer]
        else:  
            permission_classes = [IsWorkspaceOwnerOrAdmin | IsChannelMember]  
        return [permission() for permission in permission_classes]

    def _get_team_name(self, role, team_name):
        """Helper method to determine the appropriate team name based on the role."""
        if role == 'reviewer':
            return 'Reviewers'
        if role == 'reviewee' and (team_name is None or team_name == ''):
            return 'Unassigned'
        if role == 'reviewee' and team_name == 'Reviewers':
            raise ValueError("Reviewers cannot have reviewees.")
        return team_name

    def get(self, request, workspace_pk, category_pk, channel_pk):
        queryset = ChannelRole.objects.filter(channel_id=channel_pk)
        email = request.query_params.get('email')
        if email is not None:
            queryset = queryset.filter(user__email=email)
        serializer = ChannelRoleSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_pk, category_pk, channel_pk):
        channel = get_object_or_404(Channel, pk=channel_pk)
        email = request.data.get('user_email')
        role = request.data.get('role', 'reviewee')
        team_name = request.data.get('team')
        if not email:
            return Response({"detail": "User email is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            team_name = self._get_team_name(role, team_name)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, email=email)
        if not user.workspace_role.filter(workspace_id=workspace_pk).exists():
            return Response({"detail": "User is not a workspace member."}, status=status.HTTP_400_BAD_REQUEST)
        team, _ = Team.objects.get_or_create(team_name=team_name, channel=channel)
        channel_role, created = ChannelRole.objects.update_or_create(
            user=user,
            channel=channel,
            team=team,
            defaults={'role': role}
        )
        return Response(
            ChannelRoleSerializer(channel_role).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def delete(self, request, workspace_pk, category_pk, channel_pk):
        email = request.data.get('user_email')
        if not email:
            return Response({"detail": "User email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.email == email:
            return Response(
                {"detail": "You cannot remove yourself from the workspace."},
                status=status.HTTP_403_FORBIDDEN
            )
        user = get_object_or_404(User, email=email)
        member = get_object_or_404(ChannelRole, user=user, channel_id=channel_pk)
        team_members = ChannelRole.objects.filter(team=member.team)
        if len(team_members) == 1:
            member.team.delete()
        member.delete()

        return Response({"detail": "Member has been removed from the channel."}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, workspace_pk, category_pk, channel_pk):
        team_data = request.data.get('team')
        print(team_data)
        print(request.data)
        email = request.data.get('user_email')
        new_role = request.data.get('role')
        if not email:
            return Response({"detail": "User email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not new_role and not team_data:
            return Response({"detail": "new_role or team is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, email=email)
        channel_role = get_object_or_404(ChannelRole, user=user, channel_id=channel_pk)
        if new_role is not None:
            channel_role.role = new_role
            try:
                team_data = self._get_team_name(new_role, team_data)
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        if team_data is not None and team_data != '':
            team, _ = Team.objects.get_or_create(team_name=team_data, channel_id=channel_pk)
            channel_role.team = team
        channel_role.save()
        serializer = ChannelRoleSerializer(channel_role)
        return Response(serializer.data, status=status.HTTP_200_OK)