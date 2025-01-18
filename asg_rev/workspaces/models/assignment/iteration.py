from django.db import models
from users.models import User 
from workspaces.models.assignment.submission import (
    Submission,
)
from workspaces.models.team import (
    Team,
)

class Iteration(models.Model):
    reviewee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='reviewee_assignments'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviewer_assignments'
    )
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='iteration_submissions'
    )
    remarks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        reviewer_usernames = ", ".join([reviewer.username for reviewer in self.reviewers.all()])
        return f"{self.assignment_title} - Reviewee: {self.reviewee.username} | Reviewers: {reviewer_usernames}"
