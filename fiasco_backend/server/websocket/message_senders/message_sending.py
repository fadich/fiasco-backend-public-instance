__all__ = [
    "send_message",
]

import asyncio

from typing import Iterable

import simplejson

from fiasco_backend.server.websocket import (
    Message,
    WebSocketResponse,
)


def send_message(
    message: Message,
    wss: Iterable[WebSocketResponse],
    target: str,
    sender: str
):
    for ws in wss:
        if ws.closed:
            continue

        asyncio.run_coroutine_threadsafe(
            ws.send_json(
                dumps=simplejson.dumps,
                data={
                    **message.to_disc(),
                    "sender": sender,
                    "target": target
                }
            ),
            asyncio.get_event_loop()
        )
