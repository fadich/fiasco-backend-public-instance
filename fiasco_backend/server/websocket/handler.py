__all__ = [
    "WebSocketHandler",
]

import asyncio
import logging

from typing import (
    Callable,
    Optional,
    Sequence,
)

import aiohttp

from aiohttp import web
from aiohttp.web_request import Request
from marshmallow import ValidationError

from .base import (
    Authorizer,
    NotAuthorizedError,
    Message,
    WebSocketConnection,
    WebSocketResponse,
    ConnectionClosedError,
)


class DefaultAuthorizer(Authorizer):

    async def authorize(self, request: Request, ws: WebSocketResponse) -> WebSocketConnection:
        return WebSocketConnection(ws=ws)


class DefaultEventListener:

    async def __call__(self, message: Message, connection: WebSocketConnection):
        logging.debug(
            f"Event <{message.event}> received by "
            f"{connection.__class__.__name__}(ws={connection.ws}, params={connection.params})"
        )


class WebSocketHandler:
    EVENT_USER_CONNECTED = "$user-connected"
    EVENT_USER_DISCONNECTED = "$user-disconnected"

    def __init__(
        self,
        authorizer: Optional[Authorizer] = None,
        event_listeners: Optional[Sequence[Callable]] = None
    ):
        if authorizer is None:
            authorizer = DefaultAuthorizer()
        if event_listeners is None:
            event_listeners = (DefaultEventListener(), )

        self._authorizer = authorizer
        self._event_listeners = event_listeners

    async def __call__(self, request: Request):
        ws = WebSocketResponse()
        await ws.prepare(request)

        try:
            connection = await self._authorizer.authorize(request=request, ws=ws)

            await self.on_user_connected(connection=connection)

            await self._read_messages(connection)
        except (ConnectionClosedError, NotAuthorizedError) as e:
            msg = str(e)
            if not ws.closed:
                await ws.send_str(msg)
                await asyncio.sleep(0.1)

            logging.info("Connection closed with message: %s", msg)
        except Exception as e:
            logging.error("An error occurred", exc_info=e)

        return web.Response()

    async def on_user_connected(self, connection: WebSocketConnection):
        message = Message(event=self.EVENT_USER_CONNECTED)
        await self._send_event(message=message, connection=connection)

    async def on_user_disconnected(self, connection: WebSocketConnection):
        message = Message(event=self.EVENT_USER_DISCONNECTED)
        await self._send_event(message=message, connection=connection)

    async def _read_messages(self, connection: WebSocketConnection):
        try:
            async for msg in connection.ws:
                if msg.type == aiohttp.WSMsgType.ERROR:
                    logging.error(f"ws connection closed with exception {connection.ws.exception()}")
                elif msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        message = Message.from_str(msg.data)
                        if message.event.startswith("$"):
                            await connection.ws.send_str("Forbidden")
                            continue

                    except ValidationError as e:
                        await connection.ws.send_json(e.messages)
                        continue

                    except Exception as e:
                        logging.exception("An error occurred", exc_info=e)
                        await connection.ws.send_str(f"An error occurred")
                        continue

                    await self._send_event(message=message, connection=connection)
        finally:
            await self._close_connection(connection)

    async def _close_connection(
        self,
        connection: WebSocketConnection,
        message: Optional[str] = None
    ):
        if not connection.ws.closed:
            if message is not None:
                await connection.ws.send_str(message)
            await connection.ws.close()

        await self.on_user_disconnected(connection=connection)

    async def _send_event(self, message: Message, connection: WebSocketConnection):
        for listener in self._event_listeners:
            await listener(message, connection)
