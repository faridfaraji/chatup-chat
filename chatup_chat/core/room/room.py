

from dataclasses import dataclass
from typing import Any
from chatup_chat.adapter.db_client import DatabaseApiClient
from chatup_chat.core import Bot
from chatup_chat.core.cache import RedisClusterJson
from flask_socketio import emit
from chatup_chat.core.message_enums import MessageType
from chatup_chat.core.util import save_message


cache = RedisClusterJson()
db_client = DatabaseApiClient()


@dataclass
class Room:
    id: str = None
    is_live: bool = False
    space_id: str = None
    admin_managed: bool = False
    conversation_id: str = None
    admin_session_id: str = None
    occupant_session_id: str = None
    ai_response: str = ""
    bot: Bot = None

    def to_dict(self):
        return {
            "id": self.id,
            "is_live": self.is_live,
            "admin_managed": self.admin_managed,
            "conversation_id": self.conversation_id,
            "admin_session_id": self.admin_session_id,
            "occupant_session_id": self.occupant_session_id,
            "space_id": self.space_id
        }

    def admin_messages_user(self, msg: str):
        self.admin_managed = True
        print("admin says: ", msg, self.occupant_session_id)
        emit("admin_response", msg, namespace="/customer", to=self.occupant_session_id)
        save_message(self, msg, MessageType.ADMIN.value)
        self.save()

    def ai_token_call_back(self, token: str, **kwargs: Any):
        self.ai_response += token
        if not self.admin_managed:
            emit("ai_response", token, namespace="/customer", to=self.occupant_session_id)

    def ai_feedback_finished(self):
        if self.admin_managed:
            emit("ai_suggestion", {
                "message": self.ai_response,
                "conversation_id": self.conversation_id
            }, namespace="/admin", to=self.admin_session_id)
        else:
            save_message(self, self.ai_response, MessageType.AI.value)

    def user_says(self, message: str):
        save_message(self, message, MessageType.USER.value)
        self.bot.converse(self)
        if self.admin_managed:
            emit("customer_response", {
                "message": message,
                "conversation_id": self.conversation_id
            }, namespace="/admin", to=self.admin_session_id)

    def set_bot(self, bot: Bot):
        self.bot = bot

    def save(self):
        cache[f"room_{self.space_id}:{self.occupant_session_id}:{self.conversation_id}"] = self.to_dict()
