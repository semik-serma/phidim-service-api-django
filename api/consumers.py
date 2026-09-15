from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import (
    Conversation,
    ConversationParticipant,
    ChatMessage,
    ChatAttachment,
    MessageReadReceipt,
    ChatPresence,
)


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")

        # Must be authenticated
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.conversation_id = self.scope["url_route"]["kwargs"][
            "conversation_id"
        ]

        # Check whether this user can access the conversation
        allowed = await self.can_access_conversation()

        if not allowed:
            await self.close(code=4003)
            return

        self.room_group_name = (
            f"chat_{self.conversation_id}"
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.set_user_online()

        await self.accept()

        # Tell everyone in this conversation that the user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_event",
                "user_id": self.user.id,
                "is_online": True,
            },
        )

        # Send connection confirmation to this client
        await self.send_json({
            "type": "connected",
            "conversation_id": self.conversation_id,
            "user_id": self.user.id,
        })

    async def disconnect(self, close_code):

        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

        if self.user and not self.user.is_anonymous:

            await self.set_user_offline()

            if hasattr(self, "room_group_name"):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "presence_event",
                        "user_id": self.user.id,
                        "is_online": False,
                    },
                )

    async def receive_json(self, content, **kwargs):

        event_type = content.get("type")

        if event_type == "send_message":
            await self.send_message(content)

        elif event_type == "typing":
            await self.typing(content)

        elif event_type == "mark_read":
            await self.mark_read(content)

        elif event_type == "edit_message":
            await self.edit_message(content)

        elif event_type == "delete_message":
            await self.delete_message(content)

        elif event_type == "ping":
            await self.send_json({
                "type": "pong"
            })

        else:
            await self.send_json({
                "type": "error",
                "message": "Unknown event type."
            })

    # ========================================================
    # SEND MESSAGE
    # ========================================================

    async def send_message(self, data):

        content = (data.get("content") or "").strip()
        attachment_id = data.get("attachment_id")

        if not content and not attachment_id:
            await self.send_json({
                "type": "error",
                "message": "Message cannot be empty."
            })
            return

        message = await self.create_message(
            content=content,
            attachment_id=attachment_id,
        )

        if not message:
            await self.send_json({
                "type": "error",
                "message": "Unable to create message."
            })
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_event",
                "message": message,
            },
        )

    async def message_event(self, event):

        await self.send_json({
            "type": "new_message",
            "message": event["message"],
        })

    # ========================================================
    # TYPING
    # ========================================================

    async def typing(self, data):

        is_typing = bool(
            data.get("is_typing", False)
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_event",
                "user_id": self.user.id,
                "username": self.user.email,
                "is_typing": is_typing,
            },
        )

    async def typing_event(self, event):

        # Don't show your own typing event back to yourself
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "typing",
            "user_id": event["user_id"],
            "username": event["username"],
            "is_typing": event["is_typing"],
        })

    # ========================================================
    # READ RECEIPT
    # ========================================================

    async def mark_read(self, data):

        message_id = data.get("message_id")

        if not message_id:
            return

        result = await create_read_receipt(
            self.user.id,
            message_id,
            self.conversation_id,
        )

        if not result:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "read_event",
                "message_id": message_id,
                "user_id": self.user.id,
                "read_at": timezone.now().isoformat(),
            },
        )

    async def read_event(self, event):

        await self.send_json({
            "type": "read_receipt",
            "message_id": event["message_id"],
            "user_id": event["user_id"],
            "read_at": event["read_at"],
        })

    # ========================================================
    # EDIT MESSAGE
    # ========================================================

    async def edit_message(self, data):

        message_id = data.get("message_id")
        content = (data.get("content") or "").strip()

        if not message_id or not content:
            return

        updated_message = await update_message(
            self.user.id,
            message_id,
            self.conversation_id,
            content,
        )

        if not updated_message:
            await self.send_json({
                "type": "error",
                "message": "Message cannot be edited."
            })
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_edited_event",
                "message": updated_message,
            },
        )

    async def message_edited_event(self, event):

        await self.send_json({
            "type": "message_edited",
            "message": event["message"],
        })

    # ========================================================
    # DELETE MESSAGE
    # ========================================================

    async def delete_message(self, data):

        message_id = data.get("message_id")

        if not message_id:
            return

        success = await soft_delete_message(
            self.user.id,
            message_id,
            self.conversation_id,
        )

        if not success:
            await self.send_json({
                "type": "error",
                "message": "Message cannot be deleted."
            })
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_deleted_event",
                "message_id": message_id,
                "deleted_by": self.user.id,
            },
        )

    async def message_deleted_event(self, event):

        await self.send_json({
            "type": "message_deleted",
            "message_id": event["message_id"],
            "deleted_by": event["deleted_by"],
        })

    # ========================================================
    # PRESENCE
    # ========================================================

    async def presence_event(self, event):

        await self.send_json({
            "type": "presence",
            "user_id": event["user_id"],
            "is_online": event["is_online"],
        })

    # ========================================================
    # PERMISSION CHECK
    # ========================================================

    @database_sync_to_async
    def can_access_conversation(self):

        try:
            conversation = Conversation.objects.get(
                id=self.conversation_id
            )
        except Conversation.DoesNotExist:
            return False

        # Current user must be a participant
        is_participant = ConversationParticipant.objects.filter(
            conversation=conversation,
            user=self.user,
        ).exists()

        if not is_participant:
            return False

        participants = list(
            ConversationParticipant.objects
            .filter(conversation=conversation)
            .select_related("user")
        )

        # ----------------------------------------------------
        # 1-to-1 CHAT
        # ----------------------------------------------------

        if not conversation.is_group:

            if len(participants) != 2:
                return False

            roles = {
                participants[0].user.role,
                participants[1].user.role,
            }

            allowed_roles = {
                "c",  # Customer
                "t",  # Technician
            }

            technician_customer = roles == allowed_roles

            technician_admin = roles == {
                "t",
                "a",
            }

            return technician_customer or technician_admin

        # ----------------------------------------------------
        # GROUP CHAT
        # ----------------------------------------------------

        # For now, every group must contain a technician.
        roles = {
            participant.user.role
            for participant in participants
        }

        if "t" not in roles:
            return False

        # Staff is not allowed into chat currently
        if "s" in roles:
            return False

        # Prevent technician-to-technician-only groups
        if roles == {"t"}:
            return False

        return True

    # ========================================================
    # ONLINE STATUS
    # ========================================================

    @database_sync_to_async
    def set_user_online(self):

        presence, created = ChatPresence.objects.get_or_create(
            user=self.user
        )

        presence.active_connections += 1
        presence.is_online = True

        presence.save(
            update_fields=[
                "active_connections",
                "is_online",
                "updated_at",
            ]
        )

    @database_sync_to_async
    def set_user_offline(self):

        presence, created = ChatPresence.objects.get_or_create(
            user=self.user
        )

        presence.active_connections = max(
            presence.active_connections - 1,
            0,
        )

        if presence.active_connections == 0:
            presence.is_online = False
            presence.last_seen = timezone.now()

            presence.save(
                update_fields=[
                    "active_connections",
                    "is_online",
                    "last_seen",
                    "updated_at",
                ]
            )
        else:
            presence.save(
                update_fields=[
                    "active_connections",
                    "updated_at",
                ]
            )

    # ========================================================
    # CREATE MESSAGE
    # ========================================================

    @database_sync_to_async
    def create_message(
        self,
        content,
        attachment_id=None,
    ):

        try:
            conversation = Conversation.objects.get(
                id=self.conversation_id
            )
        except Conversation.DoesNotExist:
            return None

        attachment = None

        if attachment_id:

            try:
                attachment = ChatAttachment.objects.get(
                    id=attachment_id,
                    uploaded_by=self.user,
                )
            except ChatAttachment.DoesNotExist:
                return None

        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
            attachment=attachment,
        )

        # Make conversation move to top of conversation list
        conversation.save()

        attachment_data = None

        if attachment:

            attachment_data = {
                "id": attachment.id,
                "name": attachment.original_name,
                "size": attachment.size,
                "url": attachment.file.url,
            }

        return {
            "id": message.id,
            "conversation": conversation.id,
            "sender": self.user.id,
            "sender_email": self.user.email,
            "content": message.content,
            "attachment": attachment_data,
            "is_deleted": message.is_deleted,
            "edited_at": message.edited_at,
            "created_at": message.created_at.isoformat(),
        }


# ============================================================
# DATABASE HELPERS
# ============================================================

@database_sync_to_async
def create_read_receipt(
    user_id,
    message_id,
    conversation_id,
):

    try:
        message = ChatMessage.objects.get(
            id=message_id,
            conversation_id=conversation_id,
        )
    except ChatMessage.DoesNotExist:
        return False

    # Don't count your own message as something you need to read
    if message.sender_id == user_id:
        return False

    MessageReadReceipt.objects.get_or_create(
        message=message,
        user_id=user_id,
    )

    return True


@database_sync_to_async
def update_message(
    user_id,
    message_id,
    conversation_id,
    content,
):

    try:
        message = ChatMessage.objects.get(
            id=message_id,
            conversation_id=conversation_id,
            sender_id=user_id,
            is_deleted=False,
        )
    except ChatMessage.DoesNotExist:
        return None

    message.content = content
    message.edited_at = timezone.now()

    message.save(
        update_fields=[
            "content",
            "edited_at",
        ]
    )

    return {
        "id": message.id,
        "content": message.content,
        "edited_at": message.edited_at.isoformat(),
    }


@database_sync_to_async
def soft_delete_message(
    user_id,
    message_id,
    conversation_id,
):

    updated = (
        ChatMessage.objects
        .filter(
            id=message_id,
            conversation_id=conversation_id,
            sender_id=user_id,
            is_deleted=False,
        )
        .update(
            is_deleted=True,
            content="",
            attachment=None,
        )
    )

    return updated > 0