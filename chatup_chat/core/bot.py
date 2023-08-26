

from attr import define, field
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.adapter.open_ai_client import chat_completion, get_user_query_embedding
from chatup_chat.core import Bot

db_client = DatabaseApiClient()


@define
class CustomerBot(Bot):
    quality_bot = field(default=None, kw_only=True)
    category_bot = field(default=None, kw_only=True)

    def converse(self):
        self.category_bot.check_category(self)
        result = chat_completion(self)
        self.quality_bot.check_quality(result, self)
        return result

    def add_context(self, message: str):
        messages = self.memory.messages[-2:]
        to_embed = " "
        for msg in messages:
            if msg["role"] == "user":
                to_embed += f"{msg['content']} "
        to_embed += message
        query_embedding = get_user_query_embedding(to_embed)
        context = db_client.get_closest_shop_doc(query_embedding, self.shop_id)
        self.memory.set_context(
            context
        )
        self.memory.set_context_question(
            to_embed
        )
