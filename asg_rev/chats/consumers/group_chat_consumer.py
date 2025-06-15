import json
from typing import Dict, Any, Optional
from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db import DatabaseError
from channels.exceptions import DenyConnection
from workspaces.models import Channel, ChannelRole
from chats.models.message import GroupMessage
from users.models import User

class GroupChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name: Optional[str] = None
        self.room_group_name: Optional[str] = None
        self.channel: Optional[Channel] = None

    async def connect(self) -> None:
        """Handle WebSocket connection."""
        try:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            if not self.room_name:
                raise DenyConnection("Room name is required")

            workspace_id, category_id, channel_id = self.room_name.split("_")
            self.room_group_name = f"group_chat_{self.room_name}"

            user = self.scope["user"]
            user_exists = await sync_to_async(User.objects.filter(email=user.email).exists)()
            if not user_exists:
                raise DenyConnection("Authentication required")

            self.channel = await sync_to_async(get_object_or_404)(Channel, id=channel_id)
            channel_role_exists = await sync_to_async(ChannelRole.objects.filter(channel=self.channel, user=user).exists)()
            if not channel_role_exists:
                raise DenyConnection("User is not a member of this channel")

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except ValueError:
            raise DenyConnection("Invalid room name format")
        except Channel.DoesNotExist:
            raise DenyConnection("Channel does not exist")
        except Exception as e:
            raise DenyConnection(f"Connection failed: {str(e)}")

    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection."""
        if self.room_group_name and self.channel_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        """Handle incoming text messages."""
        try:
            if not text_data:
                return

            await self.handle_text_message(text_data)
                
        except Exception as e:
            await self.send_error(f"Failed to process message: {str(e)}")

    async def handle_text_message(self, text_data: str) -> None:
        """Handle regular text messages."""
        try:
            data = json.loads(text_data)
            content = data.get('content', '').strip()

            if not content:
                return

            message = await self.save_message(content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'sender_name': self.scope["user"].username,
                        'sender_email': self.scope["user"].email,
                        'content': content,
                        'channel': str(self.channel.id),
                        'created_at': message.created_at.isoformat()
                    }
                }
            )
        except json.JSONDecodeError:
            await self.send_error("Invalid message format")
        except Exception as e:
            await self.send_error(f"Failed to process message: {str(e)}")

    async def save_message(self, content: str) -> GroupMessage:
        """Save a text message to the database."""
        try:
            return await sync_to_async(GroupMessage.objects.create)(
                sender=self.scope["user"],
                content=content,  # Changed from text_content to content
                channel=self.channel
            )
        except DatabaseError as e:
            raise ValueError(f"Failed to save message: {str(e)}")

    async def chat_message(self, event: Dict[str, Any]) -> None:
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps(event['message']))

    async def send_error(self, message: str) -> None:
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'error': message
        }))