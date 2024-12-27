from rest_framework.serializers import ModelSerializer, CharField
from chats.models.message import GroupMessage

class GroupMessageSerializer(ModelSerializer):
    sender_name = CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = GroupMessage
        fields = [
            'id',
            'sender',
            'sender_name',
            'text_content',
            'file',
            'created_at',
            'channel'
        ]
        read_only_fields = ['sender', 'created_at', 'channel']