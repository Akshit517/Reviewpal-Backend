from django.db import models
from django.conf import settings
from workspaces import utils
from workspaces.models.assignment.assignment import (
    Assignment,
)
from workspaces.models.team import (
    Team,
)
from users.models import (
    User,
)

class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    sender_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    content = models.TextField(
        blank=True, 
        null=True
    )
    file = models.URLField(
        null=True
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"Submission by {self.sender}[{self.sender_team}] for {self.assignment}"
    
    def clean(self):
        if self.file is None and self.content is None:
            raise ValidationError(_('File or Content should not be null'))
