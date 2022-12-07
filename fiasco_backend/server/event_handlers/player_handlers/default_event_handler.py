__all__ = [
    "DefaultPlayerEventHandler",
]

from typing import Optional

from fiasco_backend.server.event_handlers.base_event_handler import BaseEventHandler
from fiasco_backend.server.websocket import Message
from fiasco_backend.server.websocket.message_senders import PlayerMessageSender
from fiasco_backend.server.websocket.connections import PlayerConnection


class DefaultPlayerEventHandler(BaseEventHandler):
    EVENT_ERROR = "$error"

    connection: PlayerConnection

    @property
    def is_player_online(self):
        return self.player_connection_storage.is_player_online(
            room=self.connection.room,
            player=self.connection.player
        )

    async def send_message_to_player(
        self,
        message: Message,
        sender: Optional[str] = None,
        room: Optional[str] = None,
        player: Optional[str] = None,
        target: str = PlayerMessageSender.TARGET_ROOM,
    ):
        if sender is None:
            sender = self.connection.player
        if room is None:
            room = self.connection.room
        if player is None:
            player = self.connection.player

        await self.player_message_sender.send_message(
            message=message,
            connection=self.connection,
            sender=sender,
            target=target,
            room=room,
            player=player
        )

    async def handle(self):
        await self.send_message_to_player(self.message)

    async def send_error(self, error: str):
        msg = self.create_message(
            event=self.EVENT_ERROR,
            data={
                "error": error,
            }
        )

        await self.send_message_to_player(
            message=msg,
            target=self.player_message_sender.TARGET_DIRECT
        )
