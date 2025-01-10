from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from workspaces.models import Submission
from workspaces.serializers.submission_detail import SubmissionDetailSerializer

class SubmissionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        submissions = Submission.objects.filter(
            sender=request.user
        ).select_related(
            'assignment__id__category__workspace'
        )
        
        serializer = SubmissionDetailSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
