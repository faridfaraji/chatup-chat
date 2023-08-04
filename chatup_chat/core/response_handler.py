
from typing import Any
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from flask_socketio import emit
from langchain.schema import LLMResult

from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.core.message_enums import MessageType

db_client = DatabaseApiClient()


class LLMStreamHandler():
    def __init__(self) -> None:
        ...

    def on_llm_new_token(self, token: str, **kwargs: Any):
        emit("ai_response", token)
