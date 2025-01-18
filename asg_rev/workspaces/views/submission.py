from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from workspaces.models import (
    Assignment, 
    Submission,
    ChannelRole
)
from workspaces.serializers.submission import (
    SubmissionRevieweeSerializer,
    SubmissionReviewerSerializer,
)
from workspaces.serializers.iteration import (
    IterationRevieweeSerializer,
) 
from workspaces.permissions import (
    IsWorkspaceMember,
    IsWorkspaceOwnerOrAdmin,
    IsChannelMember,
    IsReviewer, 
    IsReviewee,
)

class SubmissionRevieweeView(APIView):
    permission_classes = [
        (IsWorkspaceMember & IsReviewee) |
        IsWorkspaceOwnerOrAdmin
    ]

    def get_assignment(self):
        channel_pk = self.kwargs.get('channel_pk')
        return get_object_or_404(Assignment, id=channel_pk)

    def get_team(self, request):
        channel_role = ChannelRole.objects.filter(
            user=request.user,
            channel=self.get_assignment().id
        ).first()
        if channel_role and channel_role.team:
            return channel_role.team

    def get(self, request, *args, **kwargs):
        assignment = self.get_assignment()
        team = self.get_team(request)
        submissions = Submission.objects.filter(
           # sender_team=team,
            sender_team=team,
            assignment=assignment
        )
        serializer = SubmissionRevieweeSerializer(submissions, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
        )

    def post(self, request,*args, **kwargs):
        assignment = self.get_assignment()
        serializer = SubmissionRevieweeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                sender=request.user, 
                assignment=assignment
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request , *args, **kwargs):
        assignment = self.get_assignment()

        submission = Submission.objects.filter(
            sender=request.user, 
            assignment=assignment
        ).latest('submitted_at')

        serializer = SubmissionRevieweeSerializer(
            submission, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, *args, **kwargs):
        assignment = self.get_assignment()

        try:
            submission = Submission.objects.filter(
                sender=request.user, 
                assignment=assignment
            ).latest('submitted_at')
        except Submission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SubmissionReviewerView(APIView):
    permission_classes = [
        (IsWorkspaceMember & IsReviewer) | IsWorkspaceOwnerOrAdmin
    ]

    def get_assignment(self):
        channel_pk = self.kwargs.get('channel_pk')
        return get_object_or_404(
            Assignment, 
            id=channel_pk
        )

    def get_submissions(self, assignment, team_id=None):
        if team_id:
            return Submission.objects.filter(
                sender_team=team_id, 
                assignment=assignment
            )
        return Submission.objects.filter(assignment=assignment)

    def get(self, request, *args, **kwargs):
        assignment = self.get_assignment()
        team_id = kwargs.get('team_id')

        submissions = self.get_submissions(
            assignment, 
            team_id=team_id
        )
        serializer = SubmissionReviewerSerializer(submissions, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
        )
