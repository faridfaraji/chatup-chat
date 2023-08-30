
from typing import List
import tiktoken
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.core.message_enums import MessageType
from chatup_chat.core.settings import MODEL_NAME
from chatup_chat.models.message import Message

db_client = DatabaseApiClient()


def count_tokens_messages(messages: List[dict]):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    num_tokens = 0
    for msg in messages:
        num_tokens += len(encoding.encode(msg["message"]))
    return num_tokens


def load_message(message: Message):
    if message.message_type == MessageType.USER.value:
        if message.metadata and "admin" in message.metadata:
            return {"role": "user", "content": f"admin says: {message.message}"}
        else:
            return {"role": "user", "content": f"customer asks: {message.message}"}
    elif message.message_type == MessageType.AI.value:
        return {"role": "assistant", "content": message.message}


def save_message(room, message: Message):
    room.bot.memory.add_message(message)
    db_client.add_message(room.conversation_id, message)
