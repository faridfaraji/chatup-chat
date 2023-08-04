

from requests import HTTPError
from chatup_chat.adapter.analytics_client import ChatAnalyticsApiClient
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.adapter.db_client import DatabaseApiClient

db_client = DatabaseApiClient()
chat_analytics = ChatAnalyticsApiClient()
CONVERSATIONS = {}
cache = RedisClusterJson()


def process_message(message: dict):
    if message["message_type"] == "USER":
        return {
            "role": "user",
            "content": message["message"]
        }
    else:
        return {
            "role": "assistant",
            "content": message["message"]
        }


def initiate_conversation(customer: dict):
    conv_id = customer["conversation_id"]
    shop_id = customer["shop_id"]
    conversation = None
    if conv_id:
        try:
            conversation = db_client.get_conversation(conv_id)
        except HTTPError:
            conv_id = db_client.add_conversation(shop_id)
    else:
        conv_id = db_client.add_conversation(shop_id)
    bot_temperature = db_client.get_shop_temperature(shop_id)
    messages = db_client.get_messages(conv_id)
    summary = None
    if conversation:
        summary = conversation["conversation_summary"]["summary"]
    processed_message = []
    for msg in messages:
        processed_message.append(process_message(msg))

    cache[conv_id] = {
        "conversation_id": conv_id,
        "bot_temperature": bot_temperature,
        "messages": processed_message,
        "shop_id": shop_id,
        "summary": summary
    }
    return conv_id
