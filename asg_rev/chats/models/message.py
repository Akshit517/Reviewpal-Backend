from django.db import models
from users.models import User
from chats.models.private_chat import (
    PrivateChat,
)
from workspaces.models.channel import Channel

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GroupMessage(Message):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='group_messages'
    )