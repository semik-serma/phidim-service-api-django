
from django.db import models
import uuid


class ChatGroup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    booking = models.OneToOneField(
        "api.Booking",
        on_delete=models.CASCADE,
        related_name="chatgroup"
    )

    def __str__(self):
        return self.name or str(self.id)


class ChatMessage(models.Model):
    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    user = models.ForeignKey(
        "api.CustomUser",
        on_delete=models.CASCADE,
        related_name="messages"
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.user_id}: {self.message[:40]}"
