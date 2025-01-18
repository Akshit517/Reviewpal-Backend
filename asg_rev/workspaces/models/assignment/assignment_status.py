from django.db import models
from django.core.exceptions import ValidationError

from users.models import User
from workspaces.models.team import Team
from workspaces.models.assignment.assignment import Assignment


class AssignmentStatus(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('ongoing', 'Ongoing'),
        ('incomplete', 'Incomplete'),
    )
    # reviewee = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     related_name='assignment_status_as_reviewee' 
    # )
    team = models.ForeignKey(
        Team, 
        #null=True, 
        #blank=True, 
        on_delete=models.CASCADE, 
        related_name='assignment_statuses'
    )
    #--------------
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='assignment_status' 
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='incomplete'
    )
    earned_points = models.IntegerField()

    def __str__(self):
        if reviewee is None:
            return f'{self.assignment} -> {self.reviewee_team} = {self.earned_points}'

        return f'{self.assignment} -> {self.reviewee_team} = {self.earned_points}'

    def clean(self):
        if self.earned_points > self.assignment.total_points:
            raise ValidationError(
                f'Earned points ({self.earned_points}) cannot exceed the total points '
                f'({self.assignment.total_points}) for the assignment.'
            )

    def save(self, *args, **kwargs):
        """Override save method to ensure clean is called."""
        self.full_clean()
        super().save(*args, **kwargs)