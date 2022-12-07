#!/usr/bin/env python3

import argparse
import asyncio
import logging
import sys

from aiohttp import web

from fiasco_backend import config
from fiasco_backend.server.event_handlers import (
    DefaultAdminEventHandler,
    DefaultPlayerEventHandler,

    PlayerConnectedHandler,
    PlayerDisconnectedHandler,

    GetStatisticsHandler,
    UpsertElementHandler,
    DeleteElementHandler,
)
from fiasco_backend.server.routes import healthcheck_handler
from fiasco_backend.server.websocket import (
    WebSocketHandler,
)
from fiasco_backend.server.websocket.authorizers import (
    AdminAuthorizer,
    PlayerAuthorizer,
)
from fiasco_backend.server.websocket.connection_storages import (
    AdminStorage,
    PlayerStorage,
)
from fiasco_backend.server.websocket.message_senders import (
    AdminMessageSender,
    PlayerMessageSender,
)
from fiasco_backend.server.ws_event_listeners import WSEventListener


def init_admin_event_listener(
    admin_message_sender: AdminMessageSender,
    player_message_sender: PlayerMessageSender,
    admin_connection_storage: AdminStorage,
    player_connection_storage: PlayerStorage
):
    return WSEventListener(
        admin_message_sender=admin_message_sender,
        player_message_sender=player_message_sender,
        admin_connection_storage=admin_connection_storage,
        player_connection_storage=player_connection_storage,
        event_handlers={
            WSEventListener.EVENT_DEFAULT: DefaultAdminEventHandler,
        },
    )


def init_player_event_listener(
    admin_message_sender: AdminMessageSender,
    player_message_sender: PlayerMessageSender,
    admin_connection_storage: AdminStorage,
    player_connection_storage: PlayerStorage
):
    return WSEventListener(
        admin_message_sender=admin_message_sender,
        player_message_sender=player_message_sender,
        admin_connection_storage=admin_connection_storage,
        player_connection_storage=player_connection_storage,
        event_handlers={
            WSEventListener.EVENT_DEFAULT: DefaultPlayerEventHandler,

            WSEventListener.EVENT_USER_CONNECTED: PlayerConnectedHandler,
            WSEventListener.EVENT_USER_DISCONNECTED: PlayerDisconnectedHandler,

            "get-statistics": GetStatisticsHandler,
            "upsert-element": UpsertElementHandler,
            "delete-element": DeleteElementHandler,
        },
    )


def main():
    parser = argparse.ArgumentParser(description="Run Fiasco backend server app")

    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="set debug log level")

    parser.add_argument("--host", dest="host", type=str, default="localhost", help="server host")
    parser.add_argument("--port", dest="port", type=int, default=3000, help="server port")

    parser.add_argument(
        "--aws-region", dest="aws_region", type=str, default=None, help="AWS region"
    )
    parser.add_argument(
        "--aws-access-key-id", dest="aws_access_key_id", type=str, default=None, help="AWS access key ID"
    )
    parser.add_argument(
        "--aws-secret-access-key", dest="aws_secret_access_key", type=str, default=None, help="AWS secret access key"
    )
    parser.add_argument(
        "--aws--session-token", dest="aws_session_token", type=str, default=None, help="AWS session token"
    )

    parser.add_argument(
        "--admin-api-key", dest="admin_api_key", type=str, default=None, help="Admin API Key"
    )

    config.load_from_args(parser.parse_args())

    if config.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    app = web.Application()

    admin_connection_storage = AdminStorage()
    player_connection_storage = PlayerStorage()

    admin_message_sender = AdminMessageSender(admin_connection_storage)
    player_message_sender = PlayerMessageSender(player_connection_storage)

    admin_event_listener = init_admin_event_listener(
        admin_message_sender=admin_message_sender,
        player_message_sender=player_message_sender,
        admin_connection_storage=admin_connection_storage,
        player_connection_storage=player_connection_storage,
    )

    player_event_listener = init_player_event_listener(
        admin_message_sender=admin_message_sender,
        player_message_sender=player_message_sender,
        admin_connection_storage=admin_connection_storage,
        player_connection_storage=player_connection_storage,
    )

    admin_websocket_handler = WebSocketHandler(
        authorizer=AdminAuthorizer(admin_api_key=config.admin_api_key),
        event_listeners=(admin_event_listener, )
    )

    player_websocket_handler = WebSocketHandler(
        authorizer=PlayerAuthorizer(),
        event_listeners=(player_event_listener, )
    )

    app.add_routes([
        web.get("/", player_websocket_handler),
        web.get("/adm", admin_websocket_handler),
        web.get("/_healthcheck", healthcheck_handler),
    ])

    loop = asyncio.new_event_loop()
    loop.set_debug(config.debug)

    web.run_app(app, host=config.server_host, port=config.server_port, loop=loop)

    return 0


if __name__ == "__main__":
    sys.exit(main())
