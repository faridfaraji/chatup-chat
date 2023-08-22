

from attr import define, field
from chatup_chat.core import Bot
from chatup_chat.core.chat import Chat
from chatup_chat.core.memory import Memory
from chatup_chat.core.room.room import Room


@define
class CustomerBot(Bot):
    conversation_id: str = field(default=None, kw_only=True)
    memory: Memory = field(default=Memory(), kw_only=True)
    bot_temperature: float = field(default=0, kw_only=True)
    shop_id: str = field(default=None, kw_only=True)

    def converse(self, room: Room):
        return Chat.chat(room)

    def add_context(self, message: str):
        Chat.add_context(self, message)
