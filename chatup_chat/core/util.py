
from typing import List
import tiktoken
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.core.message_enums import MessageType
from chatup_chat.core.settings import MODEL_NAME

db_client = DatabaseApiClient()


def count_tokens_messages(messages: List[dict]):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    num_tokens = 0
    for msg in messages:
        num_tokens += len(encoding.encode(msg["content"]))
    return num_tokens


def save_message(room, message: str, message_type: str):
    if message_type == MessageType.USER.value:
        room.bot.memory.add_message({"role": "user", "content": f"customer asks: {message}"})
    elif message_type == MessageType.AI.value:
        room.bot.memory.add_message({"role": "assistant", "content": message})
    elif message_type == MessageType.ADMIN.value:
        room.bot.memory.add_message({"role": "user", "content": f"admin says: {message}"})
    db_client.add_message(room.conversation_id, message, message_type)
