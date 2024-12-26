from rest_framework import status, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404 , redirect
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html

import base64
        
from users.models.user import User
from workspaces import utils
from workspaces.models.workspace import (
    Workspace, 
    WorkspaceRole,
)
from workspaces.models.category import (
    CategoryRole,
)
from workspaces.models.channel import (
    ChannelRole
)
from workspaces.serializers.workspace import (
    WorkspaceRoleSerializer, 
    WorkspaceSerializer
)
from workspaces.permissions.workspace import (
    IsWorkspaceMember, 
    IsWorkspaceOwnerOrAdmin
)

class WorkspaceViewSet(ModelViewSet):
    serializer_class = WorkspaceSerializer
    
    def get_queryset(self):
        user = self.request.user
        workspace_ids = WorkspaceRole.objects.filter(user=user).values_list('workspace', flat=True)
        return Workspace.objects.filter(id__in = workspace_ids)

    def perform_create(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.action in ['list', 'create']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsWorkspaceOwnerOrAdmin]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsWorkspaceMember]

        return super().get_permissions()

class WorkspaceMemberView(APIView):
    def get_permissions(self):
        if self.request.method in ['POST','DELETE','PUT']:
            permission_classes = [IsWorkspaceOwnerOrAdmin]
        else:  
            permission_classes = [IsWorkspaceMember]
        return [permission() for permission in permission_classes]

    def get(self, request, workspace_pk):
        queryset = WorkspaceRole.objects.filter(
            workspace_id=workspace_pk
        ).select_related('user')

        email = request.query_params.get('email')
        if email is not None:
            queryset = queryset.filter(user__email=email)
        
        serializer = WorkspaceRoleSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_pk):
        workspace = get_object_or_404(Workspace, pk=workspace_pk)
        
        user_email = request.data.get('user_email')
        role = request.data.get('role', 'workspace_member')  
        if not user_email:
            return exceptions.ValidationError("user email is required")

        user = get_object_or_404(User, email=user_email)

        token = default_token_generator.make_token(user)
        user_id = str(user.pk).encode('utf-8')
        uid = urlsafe_base64_encode(user_id)
        self.send_invitation_email(user, workspace, token, uid, role)
        return Response(
            {"detail": "Invitation has been sent to user"}, 
            status=status.HTTP_200_OK
        )
    
    def put(self, request, workspace_pk):
        user_email = request.data.get('user_email')
        new_role = request.data.get('role')
        if not user_email:
            return exceptions.ValidationError("user email is required")
        if not new_role:
            return exceptions.ValidationError("new role is required")

        user = get_object_or_404(User, email=user_email)
        workspace_role = get_object_or_404(
            WorkspaceRole, user=user, workspace_id=workspace_pk
        )

        workspace_role.role = new_role
        workspace_role.save()

        return Response(
            {"detail": f"Member's role has been updated to {new_role}."},
            status=status.HTTP_200_OK
        )


    def delete(self, request, workspace_pk):
        email = request.data.get('user_email')
        if not email:
            return exceptions.ValidationError("user email is required")
        elif request.user.email == email:
            return exceptions.PermissionDenied("you can't remove yourself from workspace")

        user = get_object_or_404(User, email=email)
        workspace_role = get_object_or_404(WorkspaceRole, user=user, workspace_id=workspace_pk)
        workspace_role.delete()

        CategoryRole.objects.filter(
            user=user, 
            category__workspace_id=workspace_pk
        ).delete()

        ChannelRole.objects.filter(
            user=user, 
            channel__category__workspace_id=workspace_pk
        ).delete()

        return Response(
            {"detail": "Member has been removed from the all workspace related components"}, 
            status=status.HTTP_204_NO_CONTENT
        )

    def send_invitation_email(self, user, workspace, token, uid, role):
        accept_url = reverse(
            'accept_workspace_invite', 
            kwargs={
                'workspace_pk': workspace.pk, 
                'token': token,         
                'uidb64': uid,    
                'role': role 
            }, 
        )
        print(accept_url)
        invite_url=f"http://{settings.MY_DOMAIN}{accept_url}"

        subject = "Invitation to join the Workspace"
        html_content = format_html(
            """
            <p>Hello {username},</p>
            <p>You have been invited to join a workspace. Click the link below to accept the invitation:</p>
            <p><a href="{invite_url}" style="color: blue; text-decoration: underline;">Accept Invitation</a></p>
            <p>If you did not request this, please ignore this email.</p>
            """,
            username=user.username,
            invite_url=invite_url,
        )
        email = EmailMultiAlternatives(subject, "", None, [user.email])
        email.attach_alternative(html_content, "text/html")
        email.send()

from django.views import View
from django.shortcuts import render

class AcceptWorkspaceInviteView(View):
    template_name = 'workspace/invite_result.html'
    
    def get(self, request, workspace_pk, token, uidb64, role):
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = get_object_or_404(User, pk=uid)
            
            if not default_token_generator.check_token(user, token):
                return render(request, self.template_name, {
                    'error': 'Invalid or expired token'
                })
            
            workspace = get_object_or_404(Workspace, pk=workspace_pk)
            
            if WorkspaceRole.objects.filter(user=user, workspace=workspace).exists():
                return render(request, self.template_name, {
                    'error': 'You are already a member of the workspace.'
                })
            
            WorkspaceRole.objects.create(user=user, workspace=workspace, role=role)
            
            return render(request, self.template_name, {
                'message': 'You have successfully joined the workspace!',
                'workspace_name': workspace.name
            })
            
        except Exception as e:
            return render(request, self.template_name, {
                'error': str(e)
            })