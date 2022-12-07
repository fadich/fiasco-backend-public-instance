
class WebSocketError(Exception):
    pass


class NotAuthorizedError(WebSocketError):
    pass


class ConnectionClosedError(WebSocketError):
    pass
