__all__ = [
    "WebSocketResponse",
]


from aiohttp import web


class WebSocketResponse(web.WebSocketResponse):

    def __eq__(self, other):
        """Identify client responses for correctly removing/closing etc."""
        return id(self) == id(other)
