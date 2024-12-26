import json
import base64
import struct
from typing import Dict, Any, Optional, Tuple
from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.db import DatabaseError
from channels.exceptions import DenyConnection
from workspaces.models import Channel, ChannelRole
from chats.models.message import GroupMessage
from users.models import User

class GroupChatConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for handling group chat functionality."""

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
        """Route incoming messages based on type."""
        try:
            if not text_data:
                return

            if text_data[0] == 'B':
                await self.handle_file_upload(text_data[1:])
            else:
                await self.handle_text_message(text_data)
                
        except Exception as e:
            await self.send_error(f"Failed to process message: {str(e)}")

    async def handle_file_upload(self, data: str) -> None:
        """Handle file uploads sent as base64 encoded data."""
        try:
            header, file_data = self._extract_file_header_and_data(data)
            if not header or not file_data:
                raise ValueError("Invalid file data format")

            file_name = header.get('file_name')
            if not file_name:
                raise ValueError("File name is required")

            # Save file and create message
            message = await self.save_file(file_name, file_data)

            # Broadcast file message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_file",
                    "message": {
                        "sender": self.scope["user"].username,
                        "file_name": file_name,
                        "message_id": message.id if message else None
                    }
                }
            )

        except Exception as e:
            await self.send_error(f"File upload failed: {str(e)}")

    def _extract_file_header_and_data(self, data: str) -> Tuple[Dict[str, str], str]:
        """Extract the header and file data from the incoming message."""
        try:
            header_length = struct.unpack("!I", base64.b64decode(data[:8]))[0]
            
            header_end = 8 + header_length
            header_json = base64.b64decode(data[8:header_end]).decode('utf-8')
            header = json.loads(header_json)

            file_data = data[header_end:]

            return header, file_data

        except Exception as e:
            raise ValueError(f"Failed to extract file data: {str(e)}")

    async def save_file(self, file_name: str, file_data: str) -> Optional[GroupMessage]:
        """Save the file and create a message record."""
        try:
            content = base64.b64decode(file_data)
            file_content = ContentFile(content, name=file_name)

            message = await sync_to_async(GroupMessage.objects.create)(
                sender=self.scope["user"],
                channel=self.channel,
                text_content=f"File: {file_name}",
                file=file_content
            )
            return message

        except DatabaseError as e:
            raise ValueError(f"Failed to save file: {str(e)}")

    async def handle_text_message(self, text_data: str) -> None:
        """Handle regular text messages."""
        try:
            data = json.loads(text_data)
            content = data.get('message', '').strip()

            if not content:
                return

            message = await self.save_message(content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'sender': self.scope["user"].email,
                        'content': content,
                        'message_id': message.id if message else None
                    }
                }
            )

        except json.JSONDecodeError:
            await self.send_error("Invalid message format")
        except Exception as e:
            await self.send_error(f"Failed to process message: {str(e)}")

    async def save_message(self, content: str) -> Optional[GroupMessage]:
        """Save a text message to the database."""
        try:
            return await sync_to_async(GroupMessage.objects.create)(
                sender=self.scope["user"],
                text_content=content,
                channel=self.channel
            )
        except DatabaseError as e:
            raise ValueError(f"Failed to save message: {str(e)}")

    async def chat_message(self, event: Dict[str, Any]) -> None:
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps(event['message']))

    async def chat_file(self, event: Dict[str, Any]) -> None:
        """Send file message to WebSocket."""
        await self.send(text_data=json.dumps(event['message']))

    async def send_error(self, message: str) -> None:
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'error': message
        }))

