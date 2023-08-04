from attr import define, field
from chatup_chat.core.bot import CustomerBot
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.memory import Memory

cache = RedisClusterJson()


def load_chat_bot(conversation_id: str):
    bot_data = cache[conversation_id]
    if bot_data:
        bot_data["memory"] = Memory(
            messages=bot_data["messages"],
            summary=bot_data["summary"]
        )
        del bot_data["messages"]
        del bot_data["summary"]
        customer_service_bot = CustomerBot(
            **bot_data
        )
        customer_service_bot.memory.bot = customer_service_bot
        customer_service_bot.memory.initiate_system_message()
        return customer_service_bot
    return CustomerBot(conversation_id=conversation_id)
