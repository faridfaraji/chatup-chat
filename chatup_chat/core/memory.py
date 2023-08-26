

from typing import List
from attr import define, field
from chatup_chat.adapter.db_client import DatabaseApiClient

from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.util import count_tokens_messages


cache = RedisClusterJson()
db_client = DatabaseApiClient()


@define
class Memory:
    messages: List[dict] = field(default=None, kw_only=True)

    def add_message(self, message: str):
        if self.messages is None:
            self.messages = []
        self.messages.append(message)

    def get_messages(self):
        return self.messages


class MemoryManager:
    @classmethod
    def save_messages(cls, bot, messages: List[dict]):
        cache[bot.conversation_id] = {
            "conversation_id": bot.conversation_id,
            "messages": messages,
            "summary": bot.memory.summary,
            "bot_temperature": bot.bot_temperature,
            "shop_id": bot.shop_id
        }


@define
class BotMemory(Memory):
    summary: str = field(default=None, kw_only=True)
    bot = field(default=None, kw_only=True)
    initial_system_message: dict = field(default=None, kw_only=True)
    context = field(default=None, kw_only=True)
    context_question = field(default=None, kw_only=True)

    def initiate_system_message(self):
        prompt: str = db_client.get_prompt()
        negative_keywords = db_client.get_negative_keywords(self.bot.shop_id)
        self.initial_system_message = {
            "role": "system",
            "content": prompt.format(negativeKeyWords=negative_keywords)
        }

    def add_message(self, message: str):
        self.messages.append(message)
        if count_tokens_messages(self.messages) > 12000:
            self.messages = self.messages[1:]
        MemoryManager.save_messages(self.bot, self.messages)

    def add_messages(self, messages: List[dict]):
        for message in messages:
            self.add_message(message)

    def get_messages(self):
        messages = []
        if self.initial_system_message:
            messages.append(self.initial_system_message)
        if self.context:
            messages.append(self.get_context())
        if self.summary:
            messages.append({"role": "system", "content": f"here is a summary of conversation so far: {self.summary}"})
        messages.extend(self.messages)
        return messages

    def set_context(self, context: dict):
        self.context = context

    def set_context_question(self, context_question: dict):
        self.context_question = context_question

    def get_context(self):
        return {
            "role": "system",
            "content": f"HERE IS FACTUAL STORE INFORMATION THAT YOU USE TO ANSWER THE USER WITH IF YOU CANT ANSWER THE CUSTOMER BASED ON THESE THEN SIMPLY TELL THE CUSTOMER TO CONTACT STORE DIRECTLY. ONLY ANSWER BASED ON THESE INFO AND DO NOT MAKE UP ANY FACTS:\n\n {self.context}"
        }
