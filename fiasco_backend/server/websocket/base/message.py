__all__ = [
    "Message",
]


from dataclasses import dataclass
from typing import Optional, Dict, Any

from marshmallow import Schema, fields


class MessageSchema(Schema):
    event = fields.String(required=True)
    data = fields.Dict(required=False)


@dataclass
class Message:
    event: str
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_str(cls, msg: str):
        return cls(
            **MessageSchema().loads(msg)
        )

    def to_disc(self):
        return MessageSchema().dump(self)
