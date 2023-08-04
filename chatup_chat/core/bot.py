

from attr import define, field
from chatup_chat.core import Bot
from chatup_chat.core.chat import Chat
from chatup_chat.core.memory import Memory


def save_messages(func):
    def wrapper(*args, **kwargs):
        # retrieve the bot from the arguments
        bot = args[0]
        message: str = args[1]  # adjust the index based on the position of 'bot' in the arguments
        bot.memory.add_message({"role": "user", "content": message})
        # call the function
        result = func(*args, **kwargs)
        bot.memory.add_message({"role": "assistant", "content": result})

        return result
    return wrapper


@define
class CustomerBot(Bot):
    conversation_id: str = field(default=None, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)
    bot_temperature: float = field(default=0, kw_only=True)
    shop_id: str = field(default=None, kw_only=True)
    current_message: str = field(default=None, kw_only=True)

    @save_messages
    def converse(self, message: str):
        self.current_message = message
        Chat.add_context(self)
        return Chat.chat(self)
