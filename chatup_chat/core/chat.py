
from chatup_chat.adapter.analytics_client import ChatAnalyticsApiClient
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.adapter.open_ai_client import chat_completion, get_user_query_embedding
from chatup_chat.core import Bot
from chatup_chat.core.room.room import Room


chat_analytics = ChatAnalyticsApiClient()
db_client = DatabaseApiClient()


class Chat:

    @classmethod
    def chat(cls, room: Room):
        result = chat_completion(room, stream=True)
        # chat_analytics.submit_conversation_analytics(room.conversation_id)
        return result

    @classmethod
    def add_context(cls, bot: Bot, message: str):
        messages = bot.memory.messages[-2:]
        to_embed = " "
        for msg in messages:
            if msg["role"] == "user":
                to_embed += f"{msg['content']} "
        to_embed += message
        query_embedding = get_user_query_embedding(to_embed)
        context = db_client.get_closest_shop_doc(query_embedding, bot.shop_id)
        bot.memory.set_context(
            {
                "role": "system",
                "content": f"HERE IS FACTUAL STORE INFORMATION THAT YOU USE TO ANSWER THE USER WITH, ONLY ANSWER BASED ON THESE INFO AND DO NOT MAKE UP ANY FACTS:\n\n {context}"
            }
        )
