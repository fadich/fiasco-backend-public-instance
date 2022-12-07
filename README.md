# Fiasco Backend

- [Running Locally](#running-locally)
- [WebSocket Events](#websocket-events)
    - [Server Events](#server-events)
        - [Initial](#initial)
        - [Player Connected](#player-connected)
        - [Player Disconnected](#player-disconnected)
        - [Error](#error)
    - [Custom Events](#custom-events)
        - [Get Statistics](#get-statistics)
        - [Upsert Element](#upsert-element)
- [Endpoints](#endpoints)
    - [Roll Dice](#roll-dice)

## Running Locally

Build the package:
```shell
python setup.py install
```

Run the web-server:
```shell
fiasco-backend
```

Or for running the source (non-built package) code:
```shell
python -m fiasco_backend
```

Use `--help` flag for more details:
```shell
$ python -m fiasco_backend --help

usage: __main__.py [-h] [--host HOST] [--port PORT] [-d]

Run Fiasco backend server app

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  server host
  --port PORT  server port
  -d, --debug  set debug log level
```

## WebSocket Events

Connection endpoint (by default):
```text
ws://localhost:3000/?room=<ROOM_NAME>&player=<PLAYER_NAME>
```

Message structure to the server:
```json
{
  "event": "<EVENT_NAME>",
  "data": {
  }
}
```
Message structure from the server:
```json
{
  "event": "<EVENT_NAME>",
  "data": {
  },
  "sender": "<PLAYER_NAME>"
}
```

Field `data` is optional from both sides.

### Server Events

Server events are sent from server side only, on an action occurred.
They are all starts with `$` symbol and server does not pass events starting with `$` from the client.

#### Initial

Initialize data (once you joined as a player):

```json
{
  "event": "$initial",
  "sender": "<OWN_NAME>",
  "data": {
    "players": {
      "<PLAYER_1_NAME>": {
        "online": true
      },
      "<PLAYER_2_NAME>": {
        "online": false
      }
    },
    "elements": {
      "<ELEMENT_1_ID>": {
        "element_id": "<ELEMENT_1_ID>",
        "type": "dice",
        "player": "<PLAYER_1_NAME>",
        "coordinates": [0, 0]
      },
      "<ELEMENT_2_ID>": {
        "element_id": "<ELEMENT_1_ID>",
        "type": "sit",
        "player": "<PLAYER_2_NAME>",
        "coordinates": [632, 578]
      }
    }
  }
}
```

#### Player Connected

Player joined room event (first player's connection):
```json
{
  "event": "$player-connected",
  "sender": "<PLAYER_NAME>"
}
```

#### Player Disconnected

Player left room event (no active player's connection):
```json
{
  "event": "$player-disconnected",
  "sender": "<PLAYER_NAME>"
}
```


#### Error

If an error occurred, server may sends an error message like:
```json
{
  "event": "$error",
  "sender": "<PLAYER_NAME>",
  "data": {
  }
}
```

In general, it's an informative message that client may not react to.

### Custom Events

Client may send any events to the server.
If there are no registered events, server just broadcast's this message within a room, so each user connected to the room receives the message.

However, some events are being handled by the server.

#### Get Statistics

Get self-connection statistics.

Request:
```json
{
  "event": "get-statistics"
}
```

```json
{
  "event": "get-statistics",
  "data": {
    "online_time": 999
  },
  "sender": "<PLAYER_NAME>"
}
```

#### Upsert Element

Insert or Update and element.

Request:
```json
{
  "event": "upsert-element",
  "data": {
    "element_id": "<ELEMENT_ID>",
    "d": 6,
    "value": 3,
    "coordinates": [999, 666]
  }
}
```

Response:
```json
{
  "event": "upsert-element",
  "data": {
    "coordinates": [999, 666],
    "element_id": "<ELEMENT_ID>",
    "player": "666",
    "room": "123",
    "type": "Text",
    "styles": {},
    "d": 6,
    "value": 3
  },
  "sender": "<PLAYER_ID>"
}
```

#### Delete Element

Delete element in a room by Id.

Request:
```json
{
  "event": "delete-element",
  "data": {
    "element_id": "<ELEMENT_ID>"
  }
}
```

Response:
```json
{
  "event": "delete-element",
  "data": {
    "element_id": "<ELEMENT_ID>"
  },
  "sender": "<PLAYER_ID>"
}
```

## Endpoints

### Roll Dice

Roll dice. By default `d=6`. Default endpoint is:
```text
http://localhost:3000/roll?d=<DICE_SIDES>
```

Result is the number of dice roll.
