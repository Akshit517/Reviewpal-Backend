# Generated by Django 5.1.1 on 2025-01-14 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0003_alter_submission_sender_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iteration',
            name='reviewee',
        ),
    ]
