# teachers/consumers.py (replace 'teachers' with your app name)

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

online_users = set()  # Temporary in-memory store

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            user = self.scope["user"]
            online_users.add(user.id)
            await self.channel_layer.group_add("online_users", self.channel_name)
            await self.accept()
            await self.send_online_users()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            user = self.scope["user"]
            online_users.discard(user.id)
            await self.channel_layer.group_discard("online_users", self.channel_name)
            await self.send_online_users()

    async def send_online_users(self):
        # Send the updated list to everyone in the group
        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "online_users_update",
                "users": list(online_users),
            }
        )

    async def online_users_update(self, event):
        await self.send(text_data=json.dumps({
            "online_users": event["users"]
        }))
