__all__ = [
    "WebSocketConnection",
]

from time import time

from .response import WebSocketResponse


class WebSocketConnection:
    
    def __init__(self, ws: WebSocketResponse, **params):
        self._ws = ws
        self._params = params
        self._created_at = time()

    @property
    def ws(self):
        return self._ws

    @property
    def params(self):
        return self._params

    @property
    def created_at(self):
        return self._created_at
