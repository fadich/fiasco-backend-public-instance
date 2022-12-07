__all__ = [
    "healthcheck_handler",
]

from aiohttp import web


async def healthcheck_handler(*args, **kwargs):
    return web.json_response(text="I'm healthy =)")
