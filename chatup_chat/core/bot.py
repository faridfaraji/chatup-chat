

import threading
from attr import define, field
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.adapter.open_ai_client import chat_completion, get_user_query_embedding
from chatup_chat.core import Bot
from chatup_chat.core.message_enums import MessageType
from chatup_chat.models.message import Message

db_client = DatabaseApiClient()


@define
class CustomerBot(Bot):
    quality_bot = field(default=None, kw_only=True)
    category_bot = field(default=None, kw_only=True)
    inquiry_bot = field(default=None, kw_only=True)

    def converse(self):
        self.response = []
        self.inquiry_bot.check_inquiry(self)
        self.add_context()
        result = chat_completion(self)
        print("CUSTOMER ASSISTANT: ", result)
        self.memory.add_message(Message(
            message=result,
            message_type=MessageType.AI.value
        ))
        self.call_back_handler.ai_feedback_finished()
        return result

    def add_context(self):
        to_embed = self.memory.context_question
        query_embedding = get_user_query_embedding(to_embed)
        context = db_client.get_closest_shop_doc(query_embedding, self.shop_id)
        self.memory.set_context(
            context
        )
