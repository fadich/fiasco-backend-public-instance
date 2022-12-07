from aiohttp.web_request import Request

from fiasco_backend import config


def is_admin(request: Request):
    api_key = request.headers.get("ADMIN_API_KEY")

    return api_key == config.admin_api_key
