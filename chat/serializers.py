import os
import mimetypes

from rest_framework import serializers

from .models import Attachment, ChatGroup
from api.models import Booking


class AttachmentUploadSerializer(serializers.ModelSerializer):

    file = serializers.FileField(write_only=True)

    chat_group = serializers.PrimaryKeyRelatedField(
        queryset=ChatGroup.objects.all(),
        required=False,
        allow_null=True
    )

    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Attachment

        fields = [
            "id",
            "file",
            "file_url",
            "file_name",
            "file_size",
            "content_type",
            "user",
            "chat_group",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
            "file_url",
            "file_name",
            "file_size",
            "content_type",
        ]

    # --------------------------------
    # Validate chat group permissions
    # --------------------------------
    def validate_chat_group(self, value):

        user = self.context["request"].user

        if value is None:
            return value

        booking = value.booking

        # Only confirmed bookings can use chat.
        if booking.status != Booking.STATUS.CONFIRMED:
            raise serializers.ValidationError(
                "Chat is not available for this booking."
            )

        # Only booking participants can upload.
        if user.id not in (
            booking.customer_id,
            booking.technician_id
        ):
            raise serializers.ValidationError(
                "You are not authorized to upload attachments to this group."
            )

        return value

    # --------------------------------
    # Automatically assign logged user
    # --------------------------------
    def create(self, validated_data):

        validated_data["user"] = self.context["request"].user

        return super().create(validated_data)

    # --------------------------------
    # File URL
    # --------------------------------
    def get_file_url(self, obj):

        request = self.context.get("request")

        if not obj.file:
            return None

        url = obj.file.url

        if request:
            return request.build_absolute_uri(url)

        return url

    # --------------------------------
    # File name
    # --------------------------------
    def get_file_name(self, obj):

        return (
            self.context.get("uploaded_file_name")
            or os.path.basename(obj.file.name)
        )

    # --------------------------------
    # File size
    # --------------------------------
    def get_file_size(self, obj):

        return obj.file.size

    # --------------------------------
    # Content type
    # --------------------------------
    def get_content_type(self, obj):

        return (
            self.context.get("uploaded_content_type")
            or mimetypes.guess_type(obj.file.name)[0]
            or "application/octet-stream"
        )