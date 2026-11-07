from django.urls import path
from .consumers import ShareLocationConsumer

websocket_urlpatterns = [
    path(
        "ws/share-location/<int:booking_id>/",
        ShareLocationConsumer.as_asgi(),
    ),
]