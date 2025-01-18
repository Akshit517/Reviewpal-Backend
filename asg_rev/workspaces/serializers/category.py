from rest_framework import serializers
from users.models.user import User
from users.serializers.user import UserSerializer
from workspaces.models.category import (
    Category,
    CategoryRole,
)
from workspaces.models import (
    Channel,
    ChannelRole
)

from workspaces.serializers.channel import (
    ChannelSerializer,
    ChannelRoleSerializer,
)

class CategorySerializer(serializers.ModelSerializer):
    channels = serializers.SerializerMethodField()
    workspace = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'workspace', 'channels']

    def get_channels(self, obj):
        user = self.context['request'].user       

        user_channel_roles = ChannelRole.objects.filter(user=user)
        channel_ids = user_channel_roles.values_list('channel_id', flat=True)

        channels = Channel.objects.filter(
            category=obj,
            id__in=channel_ids
        )
        return ChannelSerializer(channels, many=True).data

class CategoryRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = CategoryRole
        fields = ('id', 'user', 'category', 'role')
