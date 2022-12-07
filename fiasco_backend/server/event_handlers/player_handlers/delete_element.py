__all__ = [
    "DeleteElementHandler",
]

import asyncio

from fiasco_backend.db.element import delete_element

from .default_event_handler import DefaultPlayerEventHandler


class DeleteElementHandler(DefaultPlayerEventHandler):

    async def handle(self):
        element_id = self.message.data.get("element_id")
        if element_id is None:
            await self.send_error(error="No element_id parameter provided")
            return

        msg = self.create_message(
            event=self.message.event,
            data={
                "element_id": element_id,
            }
        )
        await self.send_message_to_player(message=msg)

        asyncio.run_coroutine_threadsafe(
            delete_element(
                element_id=element_id,
                room=self.connection.room
            ),
            asyncio.get_event_loop()
        )
