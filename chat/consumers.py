
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async, aclose_old_connections

from api.models import Booking
from chat.models import ChatGroup, ChatMessage


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        # 1. Authentication
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.booking_id = self.scope["url_route"]["kwargs"]["booking_id"]

        # 2. Verify booking permissions
        self.booking = await self.get_booking_access(
            self.booking_id,
            self.user.id
        )

        if self.booking is None:
            await self.close(code=4403)
            return

        # 3. Get or create chat group
        self.chat_group = await self.get_chat_group(
            self.booking_id
        )

        self.group_name = f"chat_{self.chat_group['id']}"

        # 4. Join channel group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send_json({
            "type": "connection",
            "message": "Connected to chat group",
            "group_id": self.chat_group["id"],
            "booking_id": str(self.booking_id),
            "user_id": self.user.id
        })

        # 5. Load latest messages
        messages = await self.get_chat_history(
            self.chat_group["id"]
        )

        await self.send_json({
            "type": "chat.history",
            "messages": messages
        })

    # ------------------------------
    # Booking authorization
    # ------------------------------
    @database_sync_to_async
    def get_booking_access(self, booking_id, user_id):
        try:
            booking = Booking.objects.get(
                id=booking_id,
                status=Booking.STATUS.CONFIRMED
            )
        except (Booking.DoesNotExist, ValueError, TypeError):
            return None

        if user_id not in (
            booking.customer_id,
            booking.technician_id
        ):
            return None

        return {
            "id": str(booking.id),
            "technician_id": booking.technician_id,
            "customer_id": booking.customer_id
        }

    # ------------------------------
    # Get / create chat group
    # ------------------------------
    @database_sync_to_async
    def get_chat_group(self, booking_id):
        chat_group, created = ChatGroup.objects.get_or_create(
            booking_id=booking_id
        )

        return {
            "id": str(chat_group.id),
            "name": chat_group.name
        }

    # ------------------------------
    # Load last 30 messages
    # ------------------------------
    @database_sync_to_async
    def get_chat_history(self, group_id):
        messages = list(
            ChatMessage.objects.filter(
                group_id=group_id
            ).order_by("-created_at", "-id")[:30]
        )

        messages.reverse()

        return [
            {
                "id": msg.id,
                "group_id": str(msg.group_id),
                "user_id": msg.user_id,
                "message": msg.message,
                "created_at": msg.created_at.isoformat(),
                "updated_at": msg.updated_at.isoformat()
            }
            for msg in messages
        ]

    # ------------------------------
    # Save message to database
    # ------------------------------
    @database_sync_to_async
    def save_message(self, message):
        chat_message = ChatMessage.objects.create(
            group_id=self.chat_group["id"],
            user_id=self.user.id,
            message=message
        )

        return {
            "id": chat_message.id,
            "group_id": str(chat_message.group_id),
            "user_id": chat_message.user_id,
            "message": chat_message.message,
            "created_at": chat_message.created_at.isoformat(),
            "updated_at": chat_message.updated_at.isoformat()
        }

    # ------------------------------
    # Receive client messages
    # ------------------------------
    async def receive_json(self, content, **kwargs):

        if not isinstance(content, dict):
            await self.send_json({
                "type": "error",
                "message": "Invalid payload"
            })
            return

        event_type = content.get("type")

        if event_type in ("typing.start", "typing.stop"):
            await aclose_old_connections()

            access = await self.get_booking_access(
                self.booking_id,
                self.user.id,
            )

            if access is None:
                await self.close(code=4403)
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_typing",
                    "user_id": self.user.id,
                    "is_typing": event_type == "typing.start",
                },
            )
            return

        if event_type != "chat.message":
            await self.send_json({
                "type": "error",
                "message": "Unsupported event type"
            })
            return

        message = content.get("message")

        # Validate message type
        if not isinstance(message, str):
            await self.send_json({
                "type": "error",
                "message": "Message must be a string"
            })
            return

        message = message.strip()

        if not message:
            await self.send_json({
                "type": "error",
                "message": "Message cannot be empty"
            })
            return

        if len(message) > 5000:
            await self.send_json({
                "type": "error",
                "message": "Message exceeds 5000 characters"
            })
            return

        # Recheck booking status and access
        await aclose_old_connections()

        booking = await self.get_booking_access(
            self.booking_id,
            self.user.id
        )

        if booking is None:
            await self.send_json({
                "type": "error",
                "message": "Booking is no longer available for chat"
            })
            await self.close(code=4403)
            return

        # Save before broadcast
        saved_message = await self.save_message(message)

        # Broadcast to everyone in booking group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "data": saved_message
            }
        )

    # ------------------------------
    # Receive group broadcast
    # ------------------------------
    async def chat_message(self, event):
        await self.send_json({
            "type": "chat.message",
            "data": event["data"]
        })

        # Typing indicator event handler
    async def chat_typing(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": (
                "typing.start"
                if event["is_typing"]
                else "typing.stop"
            ),
            "user_id": event["user_id"]
        })

    # ------------------------------
    # Disconnect
    # ------------------------------
    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
