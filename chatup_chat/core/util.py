
from typing import List
import tiktoken
from chatup_chat.core.settings import MODEL_NAME


def count_tokens_messages(messages: List[dict]):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    num_tokens = 0
    for msg in messages:
        num_tokens += len(encoding.encode(msg["content"]))
    return num_tokens
