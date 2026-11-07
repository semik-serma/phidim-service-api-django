
from django.db import models
import uuid
from django.core.exceptions import ValidationError

def validate_file_size(value):
    limit = 10 * 1024 * 1024  # 10 MB in bytes
    if value.size > limit:
        raise ValidationError('File too large. Maximum size is 10MB.')


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

    is_active = models.BooleanField(default = True)

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

    is_archived = models.BooleanField(default = False)

    archived_at = models.DateTimeField(null = True)
    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.user_id}: {self.message[:40]}"


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/',validators=[validate_file_size])
    user = models.ForeignKey('api.CustomUser',on_delete=models.CASCADE,related_name='attachments')
    chat_group = models.ForeignKey(ChatGroup,on_delete=models.CASCADE,related_name='attachments',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
