from rest_framework import serializers

from workspaces.models import Submission

class SubmissionDetailSerializer(serializers.ModelSerializer):
    workspace = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['workspace', 'category', 'channel', 'submissions']

    def get_workspace(self, obj):
        workspace = obj.assignment.id.category.workspace
        return {
            'id': str(workspace.id),
            'name': workspace.name,
        }
    
    def get_category(self, obj):
        return {
            'id': str(obj.assignment.id.category.id),
            'name': obj.assignment.id.category.name
        }
    
    def get_channel(self, obj):
        channel = obj.assignment.id
        return {
            'id': str(channel.id),
            'name': channel.name
        }
    
    def get_submissions(self, obj):
        return {
            'content': obj.content,
            'file': obj.file,
            'submitted_at': obj.submitted_at
        }