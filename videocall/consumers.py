import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Tracks how many users are in each room (dev only; see note below)
ROOMS = {}


class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"call_{self.room_name}"

        # Enforce 1-1: reject a third person
        count = ROOMS.get(self.group_name, 0)
        if count >= 2:
            await self.close(code=4001)
            return

        ROOMS[self.group_name] = count + 1
        self.joined = True

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Tell this user how many people are in the room (including them)
        await self.send(json.dumps({
            "type": "joined",
            "count": ROOMS[self.group_name],
        }))

        # Tell the other person that someone arrived
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "relay",
                "sender": self.channel_name,
                "payload": {"type": "peer-joined"},
            },
        )

    async def disconnect(self, close_code):
        if not getattr(self, "joined", False):
            return

        ROOMS[self.group_name] = max(0, ROOMS.get(self.group_name, 1) - 1)
        if ROOMS[self.group_name] == 0:
            ROOMS.pop(self.group_name, None)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "relay",
                "sender": self.channel_name,
                "payload": {"type": "peer-left"},
            },
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Only relay the message types we expect
        if data.get("type") not in ("offer", "answer", "ice-candidate"):
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "relay",
                "sender": self.channel_name,
                "payload": data,
            },
        )

    async def relay(self, event):
        # Don't echo a message back to the person who sent it
        if event["sender"] == self.channel_name:
            return
        await self.send(json.dumps(event["payload"]))