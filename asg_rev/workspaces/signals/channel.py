from django.db.models.signals import post_save
from django.dispatch import receiver

from workspaces.models import (
    Channel,
    ChannelRole,
    Team
)
from workspaces import utils 

@receiver(post_save, sender=Channel)
def create_rolechannel(sender, instance, created, **kwargs):
    if created:      
        user = utils.get_current_user_or_none() 
        ChannelRole.objects.create(
            user=user, 
            channel=instance, 
            role='reviewer', 
            team=Team.objects.create(team_name='Reviewers',channel=instance)
        )
