from rest_framework import serializers
from rest_framework import exceptions 
from users.models.user import User
from users.serializers import UserSerializer
from workspaces.models import (
    Workspace,
    Category,
    Channel,
    ChannelRole,
    Assignment,
    Task,
)
from workspaces.serializers.assignment import (
    AssignmentSerializer
)
from workspaces.serializers.team import TeamSerializer

class ChannelSerializer(serializers.ModelSerializer):
    assignment_data = AssignmentSerializer(write_only=True, required=True)
    assignment = AssignmentSerializer(read_only=True)

    class Meta:
        model = Channel
        fields = [
            'id',
            'name', 
            'assignment_data',
            'assignment'
        ]
        read_only_fields = [
            'category'
        ]
            
    def validate(self, data):
        category_id = self.context['view'].kwargs.get('category_pk')
        workspace_id = self.context['view'].kwargs.get('workspace_pk')
        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except:
            raise serializers.ValidationError("workspace does not exist")
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError("category does not exist")
        data['category'] = category
        return data

    def create(self, validated_data):
        assignment_data = validated_data.pop('assignment_data', {})

        channel = Channel.objects.create(**validated_data)
        
        if assignment_data:
            assignment = Assignment.objects.create(
                id=channel,
                description=assignment_data.get('description', ''),
                total_points=assignment_data.get('total_points', 0),
                for_teams=assignment_data.get('for_teams', False)
            )
            tasks_data = assignment_data.pop('tasks',[])

            for task_data in tasks_data:
                Task.objects.create(assignment=assignment, **task_data)
        return channel

    def delete(self):
        channel = self.instance
        try:
            channel.assignment.delete()
        except Assignment.DoesNotExist:
            return serializers.ValidationError("assignment does not exist")
        channel.delete()

class ChannelRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    team = TeamSerializer()
    class Meta:
        model = ChannelRole
        fields = ('id', 'user', 'channel', 'role', 'team')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ChannelRole.objects.all(),
                fields=['user', 'channel']
            )
        ]
