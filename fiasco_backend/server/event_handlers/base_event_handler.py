__all__ = [
    "BaseEventHandler",
]

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

from fiasco_backend.server.websocket import (
    Message,
    WebSocketConnection,
)
from fiasco_backend.server.websocket.connection_storages import (
    AdminStorage,
    PlayerStorage,
)
from fiasco_backend.server.websocket.message_senders import (
    AdminMessageSender,
    PlayerMessageSender,
)


class BaseEventHandler(ABC):

    def __init__(
        self,
        admin_message_sender: AdminMessageSender,
        player_message_sender: PlayerMessageSender,
        admin_connection_storage: AdminStorage,
        player_connection_storage: PlayerStorage,
        message: Message,
        connection: WebSocketConnection
    ):
        self.admin_message_sender = admin_message_sender
        self.player_message_sender = player_message_sender

        self.admin_connection_storage = admin_connection_storage
        self.player_connection_storage = player_connection_storage

        self.message = message
        self.connection = connection

    @abstractmethod
    async def handle(self):
        raise NotImplemented()

    async def send_message_to_player(
        self,
        message: Message,
        sender: str,
        room: str,
        player: str,
        target: str = PlayerMessageSender.TARGET_ROOM,
    ):
        await self.player_message_sender.send_message(
            message=message,
            connection=self.connection,
            sender=sender,
            target=target,
            room=room,
            player=player
        )

    async def send_message_to_admin(
        self,
        message: Message,
        target: str = AdminMessageSender.TARGET_DIRECT,
        sender: str = "$ADMIN"
    ):
        await self.admin_message_sender.send_message(
            message=message,
            connection=self.connection,
            sender=sender,
            target=target,
        )

    @classmethod
    def create_message(
        cls,
        event: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Message:
        return Message(
            event=event,
            data=data
        )
