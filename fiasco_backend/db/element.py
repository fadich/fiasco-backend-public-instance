"""
Database managing functionality.

...
"""

import asyncio
import json
import logging
import time

from decimal import Decimal
from random import randint

from typing import Dict, Any, Tuple, Optional

import aioboto3
import simplejson

from marshmallow import Schema, fields, INCLUDE

from fiasco_backend import config


ELEMENTS_TABLE_NAME = "fiasco-elements"


class ElementUpdateQueue:
    PROCESSING_KEY = "__processing__"

    def __init__(self):
        self._element_queue: Dict[str, Tuple[Optional[Dict[str, Any]], Optional[float]]] = {}

    def put(self, element_data: Dict[str, Any]):
        logging.debug("Data into update queue #%s", element_data)

        element_id = element_data["element_id"]
        element_data[self.PROCESSING_KEY] = False
        if self.exists(element_id):
            if self.get(element_id)[0] is None:  # Skip, if deleted
                logging.debug("Skipping element update #%s", element_id)
                return

            stored_element_data, _ = self.get(element_id=element_id)
            element_data = {
                **stored_element_data,
                **element_data,
            }

        self._element_queue[element_id] = (element_data, time.time())

        logging.debug("Element in queue %s, %s", *self._element_queue[element_id])

    def get(self, element_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[float]]:
        element, timestamp = self._element_queue[element_id]

        processing = element.pop(self.PROCESSING_KEY)

        logging.debug("Element selected from update queue %s", element)

        try:
            return element, timestamp
        finally:
            element[self.PROCESSING_KEY] = processing

    def exists(self, element_id: str) -> bool:
        return element_id in self._element_queue

    def is_processing(self, element_id: str):
        element, _ = self._element_queue[element_id]
        if element is None:
            return True

        return element.get(self.PROCESSING_KEY, False)

    def process(self, element_id: str):
        element, _ = self._element_queue[element_id]
        if element is None:
            return

        element[self.PROCESSING_KEY] = True
        self.put(element)

    def drop(self, element_id: str):
        del self._element_queue[element_id]


element_update_queue = ElementUpdateQueue()


class ElementSchema(Schema):
    element_id = fields.String(required=True)
    room = fields.String(required=True)
    player = fields.String(required=False)
    type = fields.String(required=False)
    coordinates = fields.List(fields.Integer(), required=False)
    styles = fields.Dict(required=False)

    class Meta:
        unknown = INCLUDE


async def get_element(element_id: str, room: str):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        aws_session_token=config.aws_session_token
    ) as dynamo_resource:
        table = await dynamo_resource.Table(ELEMENTS_TABLE_NAME)

        try:
            return (await table.get_item(Key={
                "element_id": element_id,
                "room": room,
            })).get("Item", None)
        except Exception as e:
            logging.exception("Error on get_item", exc_info=e)


async def update_element_task(element_id: str, save_delay_time: float = 1.6):
    logging.debug("Update Element task started")
    await asyncio.sleep(save_delay_time * (1 + randint(2, 40) / 10))  # Sleep 2-40% longer...

    if not element_update_queue.exists(element_id=element_id):
        logging.debug("Element #%s not found in queue", element_id)
        return

    if element_update_queue.is_processing(element_id=element_id):
        logging.debug("Element #%s is already being processed", element_id)
        return

    element_data, timestamp = element_update_queue.get(element_id)
    previous_updated_diff = time.time() - timestamp

    if timestamp is None or previous_updated_diff < save_delay_time:
        logging.debug("Skipping element update; previous_updated_diff=%s < %s", previous_updated_diff, save_delay_time)
        return

    element_update_queue.process(element_id=element_id)

    elem = await get_element(
        element_id=element_data["element_id"],
        room=element_data["room"]
    )

    elem = {
        **(elem or {}),
        **element_data,
    }
    if "player" not in elem:
        logging.error("Field 'player' not found in %s", elem)
        element_update_queue.drop(element_id=element_id)
        return

    logging.info("Updating element data %s", element_data)

    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        aws_session_token=config.aws_session_token
    ) as dynamo_resource:
        table = await dynamo_resource.Table(ELEMENTS_TABLE_NAME)

        try:
            await table.put_item(Item=elem)
        except Exception as e:
            logging.exception("Error on element update", exc_info=e)
        finally:
            element_update_queue.drop(element_id=element_id)

    # TODO: Send message after updated!


async def upsert_element(element: Dict[str, Any], create: bool = False):
    data = json.loads(simplejson.dumps(element), parse_float=Decimal)

    if create:
        session = aioboto3.Session()
        async with session.resource(
            "dynamodb",
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            aws_session_token=config.aws_session_token
        ) as dynamo_resource:
            table = await dynamo_resource.Table(ELEMENTS_TABLE_NAME)

            try:
                await table.put_item(Item=data)
            except Exception as e:
                logging.exception("Error on element creation", exc_info=e)
    else:
        element_update_queue.put(element_data=data)
        await update_element_task(element_id=data["element_id"])

    return element


async def delete_element(element_id: str, room: str):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        aws_session_token=config.aws_session_token
    ) as dynamo_resource:
        if element_update_queue.exists(element_id=element_id):
            element_update_queue.drop(element_id=element_id)

        table = await dynamo_resource.Table(ELEMENTS_TABLE_NAME)

        try:
            return await table.delete_item(Key={
                "element_id": element_id,
                "room": room,
            })
        except Exception as e:
            logging.exception("Error on delete_element", exc_info=e)


async def get_room_elements(room: str):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        aws_session_token=config.aws_session_token
    ) as dynamo_resource:
        table = await dynamo_resource.Table(ELEMENTS_TABLE_NAME)

        return (await table.scan(
            FilterExpression="room = :room",
            ExpressionAttributeValues={
                ":room": room,
            }
        ))["Items"]
