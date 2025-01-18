from django.db import models

from users.models.user import User
from workspaces.models.team import Team
from workspaces.models.channel import Channel

class ChannelRole(models.Model):
    ROLE_CHOICES = [
        ('reviewer', 'Reviewer'),
        ('reviewee', 'Reviewee')
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='channel_role'
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='channel_role'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reviewer',
        blank=False
    )
    team = models.ForeignKey(
        Team,
        null=True,
        on_delete=models.CASCADE,
        related_name='team_channel_role'
    )

    class Meta:
        unique_together = ('user', 'channel')

    def save(self, *args, **kwargs):
        if self.role not in dict(self.ROLE_CHOICES).keys():
            raise ValueError(
                f"Role must be one of: {', '.join(dict(self.ROLE_CHOICES).keys())}"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.role} in {self.channel}"
