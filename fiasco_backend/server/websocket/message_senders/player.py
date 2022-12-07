__all__ = [
    "PlayerMessageSender",
]

from typing import Optional

from fiasco_backend.server.websocket import (
    WebSocketConnection,
    WebSocketError,
    Message,
)
from fiasco_backend.server.websocket.connection_storages import PlayerStorage

from .message_sending import send_message


class PlayerMessageSender:
    TARGET_DIRECT = "direct"
    TARGET_PLAYER = "player"
    TARGET_ROOM = "room"
    TARGET_BROADCAST = "broadcast"

    def __init__(self, storage: PlayerStorage):
        self._storage = storage

    async def send_message(
        self,
        message: Message,
        sender: str,
        target: Optional[str] = TARGET_ROOM,
        connection: Optional[WebSocketConnection] = None,
        room: Optional[str] = None,
        player: Optional[str] = None
    ):
        if target == self.TARGET_DIRECT:
            connections = (connection, )
        elif target == self.TARGET_PLAYER:
            connections = self._storage.get_player_connections(room=room, player=player)
        elif target == self.TARGET_ROOM:
            connections = self._storage.get_room_connections(room=room)
        elif target == self.TARGET_BROADCAST:
            connections = self._storage.get_all_connections()
        else:
            raise WebSocketError(f"Unsupported target: {target}")

        send_message(
            message=message,
            wss=(c.ws for c in connections),
            target=target,
            sender=sender
        )
