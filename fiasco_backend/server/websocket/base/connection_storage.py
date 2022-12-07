__all__ = [
    "ConnectionStorage",
]

from abc import ABC, abstractmethod

from .connection import WebSocketConnection


class ConnectionStorage(ABC):

    @abstractmethod
    def add_connection(self, connection: WebSocketConnection):
        raise NotImplementedError()

    @abstractmethod
    def remove_connection(self, connection: WebSocketConnection):
        raise NotImplementedError()
