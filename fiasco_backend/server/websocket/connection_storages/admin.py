from typing import List, Iterable

from fiasco_backend.server.websocket import (
    ConnectionStorage,
    WebSocketResponse,
)
from fiasco_backend.server.websocket.connections import AdminConnection


class AdminStorage(ConnectionStorage):

    def __init__(self):
        self._storage: List[WebSocketResponse] = []

    def add_connection(self, connection: AdminConnection):
        self._storage.append(connection.ws)

    def remove_connection(self, connection: AdminConnection):
        self._storage.remove(connection.ws)

    def get_all_connections(self) -> Iterable[AdminConnection]:
        for connection in self._storage:
            yield connection
