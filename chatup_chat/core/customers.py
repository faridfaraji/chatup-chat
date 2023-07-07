

from requests import HTTPError
from chatup_chat.core.conversations import create_conversation_chain
from chatup_chat.core.db_client import DatabaseApiClient
from chatup_chat.core.message_enums import MessageType
from chatup_chat.core.open_ai_client import get_user_query_embedding
import enum

db_client = DatabaseApiClient()

CONVERSATIONS = {}


def initiate_conversation(customer: dict):
    conv_id = customer["conversation_id"]
    shop_id = customer["shop_id"]
    if conv_id:
        try:
            db_client.get_conversation(conv_id)
        except HTTPError:
            conv_id = db_client.add_conversation(shop_id)
    else:
        conv_id = db_client.add_conversation(shop_id)
    bot_temperature = db_client.get_shop_temperature(shop_id)
    CONVERSATIONS[conv_id] = {
        "conversation_chain": create_conversation_chain(conv_id, temperature=bot_temperature),
        "shop_id": shop_id,
        "user_messages": []
    }
    return conv_id


def re_establish_conversation(conversation_id: str):
    shop_id = db_client.get_conversation(conversation_id)["shop_id"]
    bot_temperature = db_client.get_shop_temperature(shop_id)
    CONVERSATIONS[conversation_id] = {
        "conversation_chain": create_conversation_chain(conversation_id, temperature=bot_temperature),
        "shop_id": shop_id,
        "user_messages": []
    }
    return conversation_id


def respond_customer_message(conversation_id: str, message: str):
    db_client.add_message(conversation_id, message, MessageType.USER.value)
    if conversation_id in CONVERSATIONS:
        conv_chain = CONVERSATIONS[conversation_id]["conversation_chain"]
        if conv_chain is None:
            CONVERSATIONS[conversation_id]["conversation_chain"] = create_conversation_chain(conversation_id)
        CONVERSATIONS[conversation_id]["user_messages"].append(message)
        to_embed = ''.join(CONVERSATIONS[conversation_id]["user_messages"][-3:])
        query_embedding = get_user_query_embedding(to_embed)
        context = db_client.get_closest_shop_doc(query_embedding, CONVERSATIONS[conversation_id]["shop_id"])
        input = f"""{message}\nContext-Start\n================\n{context}\n===============\nContext-end"""
        user_input = input
        CONVERSATIONS[conversation_id]["conversation_chain"].predict(input=user_input)
    else:
        re_establish_conversation(conversation_id)
        respond_customer_message(conversation_id, message)