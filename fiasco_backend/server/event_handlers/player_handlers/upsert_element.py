__all__ = [
    "UpsertElementHandler",
]

import asyncio

from marshmallow import ValidationError

from fiasco_backend.db.element import (
    ElementSchema,
    upsert_element,
)
from fiasco_backend.utils.db import generate_uuid

from .default_event_handler import DefaultPlayerEventHandler


class UpsertElementHandler(DefaultPlayerEventHandler):

    async def handle(self):
        data = {
            **(self.message.data or {}),
            "room": self.connection.room,
        }

        create = False
        if data.get("element_id") is None:
            create = True
            data["element_id"] = generate_uuid()
            if data.get("player") is None:
                data["player"] = self.connection.player

        try:
            element = ElementSchema().load(data)
        except ValidationError as e:
            await self.send_error(e.messages)
            return

        msg = self.create_message(
            event=self.message.event,
            data=element
        )
        await self.send_message_to_player(msg)

        asyncio.run_coroutine_threadsafe(
            upsert_element(element, create=create),
            asyncio.get_event_loop()
        )
