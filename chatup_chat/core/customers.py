

from requests import HTTPError
from chatup_chat.adapter.analytics_client import ChatAnalyticsApiClient
from chatup_chat.core import Manager
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.adapter.db_client import DatabaseApiClient
from flask import request

from chatup_chat.core.room.room import Room
from chatup_chat.core.util import load_message
from chatup_chat.models.message import Message

db_client = DatabaseApiClient()
CONVERSATIONS = {}
cache = RedisClusterJson()


def initiate_conversation(room_manager: Manager, customer: dict):
    conv_id = customer["conversation_id"]
    shop_id = customer["shop_id"]
    metadata = customer["metadata"]
    conversation = None
    if conv_id:
        try:
            conversation = db_client.get_conversation(conv_id)
        except HTTPError:
            conv_id = db_client.add_conversation(shop_id, metadata=metadata)
    else:
        conv_id = db_client.add_conversation(shop_id, metadata=metadata)
    bot_temperature = db_client.get_shop_temperature(shop_id)
    messages: Message = db_client.get_messages(conv_id)
    summary = None
    if conversation:
        summary = conversation["conversation_summary"]["summary"]
    processed_message = []
    messages = [msg.to_dict() for msg in messages]

    cache[conv_id] = {
        "conversation_id": conv_id,
        "bot_temperature": bot_temperature,
        "messages": processed_message,
        "shop_id": shop_id,
        "summary": summary
    }
    room: Room = room_manager.get_room(shop_id, request.sid, conv_id)
    room.conversation_id = conv_id
    room_manager.occupy_room(room)
    return conv_id
