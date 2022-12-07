__all__ = [
    "AdminMessageSender",
]

from typing import Optional

from fiasco_backend.server.websocket import (
    WebSocketConnection,
    WebSocketError,
    Message,
)
from fiasco_backend.server.websocket.connection_storages import AdminStorage


from .message_sending import send_message


class AdminMessageSender:
    TARGET_DIRECT = "direct"
    TARGET_BROADCAST = "broadcast"

    def __init__(self, storage: AdminStorage):
        self._storage = storage

    async def send_message(
        self,
        message: Message,
        sender: str,
        target: Optional[str] = TARGET_DIRECT,
        connection: Optional[WebSocketConnection] = None,
    ):
        if target == self.TARGET_DIRECT:
            connections = (connection, )
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
