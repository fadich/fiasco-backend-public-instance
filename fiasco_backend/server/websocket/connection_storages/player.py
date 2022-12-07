__all__ = [
    "PlayerStorage",
]

from collections import defaultdict
from typing import Dict, List, Iterable

from fiasco_backend.server.websocket import (
    ConnectionStorage,
)
from fiasco_backend.server.websocket.connections import PlayerConnection


class PlayerStorage(ConnectionStorage):

    def __init__(self):
        self._storage: Dict[str, Dict[str, List[PlayerConnection]]] = defaultdict(lambda: defaultdict(list))

    def add_connection(self, connection: PlayerConnection):
        self._storage[connection.room][connection.player].append(connection)

    def remove_connection(self, connection: PlayerConnection):
        self._storage[connection.room][connection.player].remove(connection)

        if not self.is_room_online(room=connection.room):
            del self._storage[connection.room]
        elif not self.is_player_online(room=connection.room, player=connection.player):
            del self._storage[connection.room][connection.player]

    def is_room_online(self, room: str) -> bool:
        return room in self._storage and bool(sum(len(self._storage[room][p]) for p in self._storage[room]))

    def is_player_online(self, room: str, player: str) -> bool:
        return player in self._storage[room] and bool(len(self._storage[room][player]))

    def get_all_connections(self) -> Iterable[PlayerConnection]:
        for room, players in self._storage.items():
            for player, connections in players.items():
                for connection in connections:
                    yield connection

    def get_room_connections(self, room: str) -> Iterable[PlayerConnection]:
        for player, connections in self._storage[room].items():
            for connection in connections:
                yield connection

    def get_player_connections(self, room: str, player: str) -> Iterable[PlayerConnection]:
        for connection in self._storage[room][player]:
            yield connection
