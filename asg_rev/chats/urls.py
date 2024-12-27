from django.urls import path, include
from chats.views import ChannelMessagesView

urlpatterns = [
    path(
        f'api/workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/chat/', 
        ChannelMessagesView.as_view(), 
        name='group-chat'
    ),
]
