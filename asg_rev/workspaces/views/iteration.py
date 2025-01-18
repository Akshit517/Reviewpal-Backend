from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import ValidationError

from users.serializers import UserSerializer
from workspaces.models import (
    Submission,
    Iteration,
    AssignmentStatus
)
from workspaces.permissions import (
    IsReviewer,
    IsReviewee,
    IsTeamMember
)
from workspaces.serializers.iteration import (
    IterationReviewerSerializer,
    IterationRevieweeSerializer,
    IterationCreateSerializer,
)
from workspaces.serializers.assignment_status import (
    AssignmentStatusUpdateSerializer,
    AssignmentStatusSerializer
)
class ReviewerIterationView(APIView):
    permission_classes = [IsReviewer]

    @transaction.atomic
    def post(self, request, workspace_pk, category_pk, channel_pk, submission_id):
        """Create a new iteration with remarks and optionally update status."""
        submission = get_object_or_404(
            Submission.objects.select_related('assignment', 'sender'),
            id=submission_id
        )

        iteration_serializer = IterationCreateSerializer(data=request.data)
        if not iteration_serializer.is_valid():
            return Response(iteration_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        iteration = iteration_serializer.save(
            submission=submission,
            reviewer=request.user,
        )

        status_data = request.data.get('assignment_status')
        if status_data:
            status_serializer = AssignmentStatusUpdateSerializer(data=status_data)
            if status_serializer.is_valid():
                AssignmentStatus.objects.update_or_create(
                    assignment=submission.assignment,
                    team=submission.sender_team,
                    defaults=status_serializer.validated_data
                )

        return Response(
            IterationReviewerSerializer(iteration).data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, workspace_pk, category_pk, channel_pk, submission_id):
        """Get iteration details with submission and status information."""
        submission = get_object_or_404(Submission, id=submission_id)
        iterations = Iteration.objects.filter(
            submission=submission,
            reviewer=request.user
        ).select_related(
            'reviewee',
            'reviewer',
            'submission',
            'submission__assignment'
        )

        serializer = IterationReviewerSerializer(iterations, many=True)
        return Response(serializer.data)

class RevieweeIterationView(APIView):
    permission_classes = [( IsReviewee | IsReviewer )& IsTeamMember]

    def get(self, request, workspace_pk, category_pk, channel_pk, submission_pk):
        """Get iterations with remarks and status for reviewee."""
        submission = get_object_or_404(
            Submission,
            id=submission_pk
        )

        iterations = Iteration.objects.filter(
            submission=submission
        ).select_related(
            'reviewer',
            'submission',
            'submission__assignment'
        ).order_by('-created_at')

        serializer = IterationRevieweeSerializer(iterations, many=True)
        
        latest_status = AssignmentStatus.objects.filter(
            assignment=submission.assignment,
            team=submission.sender_team
        ).first()

        return Response({
            'iterations': serializer.data,
            'total_iterations': iterations.count(),
            'current_status': {
                'status': latest_status.status if latest_status else 'incomplete',
                'earned_points': latest_status.earned_points if latest_status else 0
            }
        })