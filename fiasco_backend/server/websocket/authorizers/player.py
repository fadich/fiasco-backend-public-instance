__all__ = [
    "PlayerAuthorizer",
]

import re

from typing import Optional

from aiohttp.web_request import Request

from fiasco_backend.server.websocket import (
    Authorizer,
    NotAuthorizedError,
    WebSocketResponse,
    WebSocketConnection,
)

from fiasco_backend.server.websocket.connections import PlayerConnection


class PlayerAuthorizer(Authorizer):

    async def authorize(self, request: Request, ws: WebSocketResponse) -> Optional[WebSocketConnection]:
        room = request.query.get("room")
        player = request.query.get("player")

        if room is None:
            raise NotAuthorizedError("No <room> provided")

        if player is None:
            raise NotAuthorizedError("No <player> provided")

        if re.search(r".*\s+.*", room):
            raise NotAuthorizedError("Invalid <room> characters")

        if re.search(r".*\s+.*", player) or player.startswith("$"):
            raise NotAuthorizedError("Invalid <player> characters")

        return PlayerConnection(
            ws=ws,
            room=room,
            player=player
        )

