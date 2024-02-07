
from abc import ABC
from typing import List
from attr import define, field
from chatup_chat.core.memory import Memory


@define
class Bot(ABC):
    conversation_id: str = field(default=None, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)
    bot_temperature: float = field(default=0, kw_only=True)
    shop_id: str = field(default=None, kw_only=True)
    call_back_handler = field(default=None, kw_only=True)
    response = field(default=None, kw_only=True)
    is_response_finished: bool = field(default=False, kw_only=True)
    is_speaking = field(default=False, kw_only=True)
    model_name: str = field(default="gpt-3.5-turbo-16k", kw_only=True)
    response_handler = field(default=None, kw_only=True)
    elder_bot = field(default=None, kw_only=True)

    def __post_init__(self):
        if self.response is None:
            self.response = []

    def speak(self):
        self.is_speaking = True

    def shutup(self):
        self.is_speaking = False

    def response_handler(self, token):
        if self.is_speaking:
            self.elder_bot.response.append(token)
            self.call_back_handler.ai_token_call_back(token)


class Manager(ABC):
    ...


@define
class Memory:
    messages: List[dict] = field(default=[], kw_only=True)

    def add_message(self, message: str):
        self.messages.append(message)

    def get_messages(self):
        return self.messages
