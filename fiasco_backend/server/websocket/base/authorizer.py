__all__ = [
    "Authorizer",
]

from abc import ABC, abstractmethod

from aiohttp.web_request import Request

from .connection import WebSocketConnection
from .response import WebSocketResponse


class Authorizer(ABC):

    @abstractmethod
    async def authorize(self, request: Request, ws: WebSocketResponse) -> WebSocketConnection:
        raise NotImplementedError()
