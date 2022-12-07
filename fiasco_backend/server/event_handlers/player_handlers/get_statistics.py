__all__ = [
    "GetStatisticsHandler",
]

from time import time

from .default_event_handler import DefaultPlayerEventHandler


class GetStatisticsHandler(DefaultPlayerEventHandler):

    async def handle(self):
        msg = self.create_message(
            event=self.message.event,
            data={
                "online_time": int(time() - self.connection.created_at),
            }
        )

        await self.send_message_to_player(msg, target=self.player_message_sender.TARGET_DIRECT)
