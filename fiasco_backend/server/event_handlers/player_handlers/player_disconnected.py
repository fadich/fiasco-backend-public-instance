__all__ = [
    "PlayerDisconnectedHandler",
]

from .default_event_handler import DefaultPlayerEventHandler


class PlayerDisconnectedHandler(DefaultPlayerEventHandler):
    EVENT_PLAYER_DISCONNECTED = "$player-disconnected"

    async def handle(self):
        self.player_connection_storage.remove_connection(self.connection)
        if not self.is_player_online:  # Has no any active connections yet
            msg = self.create_message(
                event=self.EVENT_PLAYER_DISCONNECTED
            )
            await self.send_message_to_player(msg)
