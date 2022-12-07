__all__ = [
    "AdminAuthorizer",
]

from typing import Optional

from aiohttp.web_request import Request

from fiasco_backend.server.websocket import (
    Authorizer,
    NotAuthorizedError,
    WebSocketResponse,
    WebSocketConnection,
)
from fiasco_backend.server.websocket.connections import AdminConnection


class AdminAuthorizer(Authorizer):

    def __init__(self, admin_api_key: str):
        self._admin_api_key = admin_api_key

    async def authorize(self, request: Request, ws: WebSocketResponse) -> Optional[WebSocketConnection]:
        if request.headers.get("ADMIN_API_KEY") != self._admin_api_key:
            raise NotAuthorizedError("Forbidden")

        return AdminConnection(ws=ws)
