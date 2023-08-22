
from dataclasses import dataclass
from chatup_chat.core.cache import RedisClusterJson
from flask_socketio import emit
cache = RedisClusterJson()


@dataclass
class Admin:
    session_id: str
    shop_id: str

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "shop_id": self.shop_id
        }

    def notify_admin_of_live_room(self, conversation_id: str):
        emit("live_conversations", conversation_id, namespace="/admin", to=self.session_id)

    def notify_admin_of_off_room(self, conversation_id: str):
        emit("off_conversations", conversation_id, namespace="/admin", to=self.session_id)

    def message_user(self, room, message: str):
        room.admin_messages_user(message)

    def take_over_conversation(self, room):
        room.admin_managed = True
        room.admin_session_id = self.session_id
        room.save()

