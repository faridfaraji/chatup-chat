
from typing import Any
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from flask_socketio import emit


class ChatUpStreamHandler(StreamingStdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs: Any):
        emit("ai_response", token)
