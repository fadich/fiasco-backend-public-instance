__all__ = [
    "config",
]


from argparse import Namespace
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    debug: Optional[bool] = False

    server_host: Optional[str] = "0.0.0.0"
    server_port: Optional[int] = 3000

    aws_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None

    admin_api_key: Optional[str] = None

    def load_from_args(self, namespace: Namespace):
        self.debug = namespace.debug

        self.server_host = namespace.host
        self.server_port = namespace.port

        self.aws_region = namespace.aws_region
        self.aws_access_key_id = namespace.aws_access_key_id
        self.aws_secret_access_key = namespace.aws_secret_access_key
        self.aws_session_token = namespace.aws_session_token

        self.admin_api_key = namespace.admin_api_key

        return self


config = Config()
