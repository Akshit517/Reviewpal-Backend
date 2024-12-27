from django.shortcuts import render, get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from workspaces.permissions.channel import IsChannelMember
from workspaces.models.channel import Channel 

from chats.models.message import GroupMessage
from chats.serializers.message import GroupMessageSerializer

class ChannelMessagesView(ListAPIView):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsChannelMember & IsAuthenticated]
    
    def get_queryset(self):
        channel_id = self.kwargs.get('channel_pk')
        channel = get_object_or_404(Channel, id=channel_id)
        
        return GroupMessage.objects.filter(
            channel=channel
        ).select_related(
            'sender'  
        ).order_by(
            'created_at'
        )