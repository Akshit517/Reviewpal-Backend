from rest_framework.serializers import ModelSerializer, CharField
from chats.models.message import GroupMessage

class GroupMessageSerializer(ModelSerializer):
    sender_name = CharField(source='sender.username', read_only=True)
    sender_email = CharField(source='sender.email', read_only=True)
    
    class Meta:
        model = GroupMessage
        fields = [
            'id',
            'sender_name',
            'sender_email',
            'content',
            'channel',
        ]
        read_only_fields = ['sender','channel'] 