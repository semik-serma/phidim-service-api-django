import json

from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer
)

from channels.db import database_sync_to_async

# Change this import to your actual Booking model path.
from api.models import Booking


class ShareLocationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.booking_id = self.scope["url_route"]["kwargs"]["booking_id"]

        # Check booking ownership before accepting.
        self.booking = await self.get_booking_access(
            self.booking_id,
            self.user.id,
        )

        if self.booking is None:
            await self.close(code=4403)
            return

        self.group_name = f"booking_{self.booking_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        print(self.group_name)

        await self.accept()

        await self.send_json({
            "type": "connection",
            "message": "Connected to booking location channel",
            "booking_id": self.booking_id,
        })

    @database_sync_to_async
    def get_booking_access(self, booking_id, user_id):
        try:
            booking = Booking.objects.get(
                id=booking_id,
                status=Booking.STATUS.CONFIRMED,
            )
        except Booking.DoesNotExist:
            return None

        if user_id not in (
            booking.customer_id,
            booking.technician_id,
        ):
            return None

        return {
            "id": booking.id,
            "technician_id": booking.technician_id,
            "customer_id": booking.customer_id,
        }

    async def receive_json(self, content, **kwargs):
        # Recheck authorization in case booking was
        # reassigned, cancelled, or deleted.
        access = await self.get_booking_access(
            self.booking_id,
            self.user.id,
        )
        print("received json",access)

        if access is None:
            await self.close(code=4403)
            return

        if content.get("type") != "location_update":
            await self.send_json({
                "type": "error",
                "message": "Unsupported message type",
            })
            return

        # Only the assigned technician can publish GPS.
        if self.user.id != access["technician_id"]:
            await self.send_json({
                "type": "error",
                "message": "Only the technician can share location",
            })
            return

        try:
            latitude = float(content["latitude"])
            longitude = float(content["longitude"])
            print(latitude,longitude)
        except (KeyError, TypeError, ValueError):
            await self.send_json({
                "type": "error",
                "message": "Invalid coordinates",
            })
            return

        if not (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            await self.send_json({
                "type": "error",
                "message": "Coordinates out of range",
            })
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "location.message",
                "sender_id": self.user.id,
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    async def location_message(self, event):
        # Check access again before delivering location.
        access = await self.get_booking_access(
            self.booking_id,
            self.user.id,
        )
        print("Location message",access)

        if access is None:
            await self.close(code=4403)
            return

        # Do not send the technician's location back
        # to the same technician.
        if self.user.id == event["sender_id"]:
            return

        print("Ready to send",{
            "type": "location_update",
            "booking_id": self.booking_id,
            "technician_id": event["sender_id"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
        })    
        await self.send_json({
            "type": "location_update",
            "booking_id": self.booking_id,
            "technician_id": event["sender_id"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
        })

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )