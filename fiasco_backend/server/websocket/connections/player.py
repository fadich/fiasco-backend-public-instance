__all__ = [
    "PlayerConnection",
]

from fiasco_backend.server.websocket import (
    WebSocketConnection,
    WebSocketError,
    WebSocketResponse,
)


class PlayerConnection(WebSocketConnection):

    def __init__(self, ws: WebSocketResponse, **params):
        if "room" not in params:
            raise WebSocketError("No <room> provided for player connection")

        if "player" not in params:
            raise WebSocketError("No <player> provided for player connection")

        super().__init__(ws=ws, **params)

    @property
    def room(self):
        return self._params["room"]

    @property
    def player(self):
        return self._params["player"]

