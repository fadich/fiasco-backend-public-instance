__all__ = [
    "PlayerConnectedHandler",
]

import logging
from collections import defaultdict

from fiasco_backend.db.element import delete_element, get_room_elements, element_update_queue
from .default_event_handler import DefaultPlayerEventHandler


class PlayerConnectedHandler(DefaultPlayerEventHandler):
    EVENT_INITIAL = "$initial"
    EVENT_PLAYER_CONNECTED = "$player-connected"

    async def handle(self):
        if not self.is_player_online:  # Already has active connections
            msg = self.create_message(
                event=self.EVENT_PLAYER_CONNECTED
            )
            await self.send_message_to_player(msg)

        self.player_connection_storage.add_connection(self.connection)

        await self.send_initial_data()

    async def send_initial_data(self):
        players = defaultdict(defaultdict)
        elements = {}
        items = await get_room_elements(self.connection.room)

        for item in items:
            # TODO: Remove after ws sending in update_element_task() will be implemented
            element_id = item["element_id"]
            if element_update_queue.exists(element_id=element_id):
                element, _ = element_update_queue.get(element_id=element_id)

                item = {
                    **item,
                    **element,
                }

            elements[element_id] = item
            try:
                players[item["player"]]["online"] = False
            except KeyError as e:
                logging.warning("Key error on init. Removing element #%s", element_id, exc_info=e)

                await delete_element(element_id=element_id, room=self.connection.room)

        player_connections = self.player_connection_storage.get_room_connections(
            room=self.connection.room
        )

        for connection in player_connections:
            players[connection.player]["online"] = True

        initial_message = self.create_message(
            event=self.EVENT_INITIAL,
            data={
                "players": players,
                "elements": elements,
            }
        )

        await self.send_message_to_player(
            target=self.player_message_sender.TARGET_DIRECT,
            message=initial_message
        )
