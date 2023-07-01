
from typing import Any
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from flask_socketio import emit
from langchain.schema import LLMResult

from chatup_chat.core.db_client import DatabaseApiClient
from chatup_chat.core.message_enums import MessageType

db_client = DatabaseApiClient()


class ChatUpStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, conversation_id: str) -> None:
        super().__init__()
        self.conversation_id = conversation_id

    def on_llm_new_token(self, token: str, **kwargs: Any):
        emit("ai_response", token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        response = response.generations[0][0].text
        db_client.add_message(self.conversation_id, response, MessageType.AI.value)
        # return super().on_llm_end(response, **kwargs)
    # def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
    #     ai_response = response[]
    #     db_client.add_message(self.conversation_id, response, MessageType.AI.value)

