import uuid
from django.db import models
from workspaces.models.category import Category

class Channel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=50,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='channel'
    )
