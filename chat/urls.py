from django.urls import path
from .views import AttachmentUploadAPIView

urlpatterns = [
    path(
        "attachments/upload/",
        AttachmentUploadAPIView.as_view(),
        name="attachment-upload"
    ),
]