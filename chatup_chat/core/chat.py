
from chatup_chat.adapter.analytics_client import ChatAnalyticsApiClient
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.adapter.open_ai_client import chat_completion, get_user_query_embedding
from chatup_chat.core.bot import Bot
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.message_enums import MessageType
from chatup_chat.core.response_handler import LLMStreamHandler


chat_analytics = ChatAnalyticsApiClient()
db_client = DatabaseApiClient()
cache = RedisClusterJson()


def save_messages(func):
    def wrapper(*args, **kwargs):
        # retrieve the bot from the arguments
        bot: Bot = args[1]  # adjust the index based on the position of 'bot' in the arguments
        message = bot.current_message
        db_client.add_message(bot.conversation_id, message, MessageType.USER.value)
        # call the function
        result = func(*args, **kwargs)
        db_client.add_message(bot.conversation_id, result, MessageType.AI.value)

        return result
    return wrapper


class Chat:
    call_back_handler = LLMStreamHandler()

    @classmethod
    @save_messages
    def chat(cls, bot: Bot):
        result = chat_completion(bot, call_back_handler=cls.call_back_handler, stream=True)
        chat_analytics.submit_conversation_analytics(bot.conversation_id)
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
                "content": f"HERE IS FACTUAL STORE INFORMATION THAT YOU SHOULD TRY TO USE TO ANSWER THE USER TO THE BEST OF YOUR ABILITY WITH:\n\n {context}"
            }
        )
