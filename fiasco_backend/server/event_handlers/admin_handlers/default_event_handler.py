__all__ = [
    "DefaultAdminEventHandler",
]


from fiasco_backend.server.event_handlers.base_event_handler import BaseEventHandler


class DefaultAdminEventHandler(BaseEventHandler):

    async def handle(self):
        await self.send_message_to_admin(self.message)
