import uuid

from django.db import models
from workspaces.models.channel import Channel

class Team(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    team_name = models.CharField(
        max_length=100
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='teams'
    )

    def __str__(self):
        return f"{self.team_name}"