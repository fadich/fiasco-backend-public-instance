import logging

from typing import Dict, Type

from fiasco_backend.server.event_handlers import BaseEventHandler
from fiasco_backend.server.websocket import (
    Message,
    WebSocketConnection,
    WebSocketHandler,
)
from fiasco_backend.server.websocket.connection_storages import AdminStorage, PlayerStorage
from fiasco_backend.server.websocket.message_senders import AdminMessageSender, PlayerMessageSender


class WSEventListener:
    EVENT_USER_CONNECTED = WebSocketHandler.EVENT_USER_CONNECTED
    EVENT_USER_DISCONNECTED = WebSocketHandler.EVENT_USER_DISCONNECTED
    EVENT_DEFAULT = "$default"

    def __init__(
        self,
        event_handlers: Dict[str, Type[BaseEventHandler]],
        admin_message_sender: AdminMessageSender,
        player_message_sender: PlayerMessageSender,
        admin_connection_storage: AdminStorage,
        player_connection_storage: PlayerStorage,
    ):
        self.event_handlers = event_handlers
        self.admin_message_sender = admin_message_sender
        self.player_message_sender = player_message_sender
        self.admin_connection_storage = admin_connection_storage
        self.player_connection_storage = player_connection_storage

    async def __call__(self, message: Message, connection: WebSocketConnection):
        if message.event in self.event_handlers:
            handler_cls = self.event_handlers[message.event]
        elif self.EVENT_DEFAULT in self.event_handlers:
            handler_cls = self.event_handlers[self.EVENT_DEFAULT]
        else:
            logging.debug(
                f"Event <{message.event}> received by "
                f"{connection.__class__.__name__}(ws={connection.ws}, params={connection.params})"
            )
            return

        await handler_cls(
            admin_message_sender=self.admin_message_sender,
            player_message_sender=self.player_message_sender,
            admin_connection_storage=self.admin_connection_storage,
            player_connection_storage=self.player_connection_storage,
            connection=connection,
            message=message
        ).handle()
