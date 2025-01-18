from rest_framework import serializers 
from workspaces.models import (
    Submission,
    Iteration,
    ChannelRole
)
from workspaces.serializers.iteration import (
    IterationRevieweeSerializer,   
)
from workspaces.serializers.team import (
    TeamSerializer   
)
from users.serializers import (
    UserSerializer,
)
from workspaces.models.team import Team

class SubmissionRevieweeSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Submission
        fields = ['id','content','file','submitted_at', 'sender']

    def create(self, validated_data):
        sender = validated_data.pop('sender') 
        assignment = validated_data.pop('assignment')
        sender_team = ChannelRole.objects.filter(
            user=sender,
            channel=assignment.id
        ).first().team
        submission = Submission.objects.create(
           sender=sender,
           sender_team=sender_team,
           assignment=assignment,
            **validated_data
        )

        return submission

class SubmissionReviewerSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    sender_team = TeamSerializer()
    iterations = IterationRevieweeSerializer(
        many=True, 
        read_only=True,
        source='iteration_submissions'
    )
    content = serializers.CharField(
        read_only=True
    )
    file = serializers.URLField(
        read_only=True
    )
    
    class Meta:
        model = Submission
        fields ='__all__'
