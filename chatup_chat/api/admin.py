from __future__ import annotations

from flask_socketio import Namespace, emit
from chatup_chat.api.models.customer import AdminMessageSchema, CustomerSchema, MessageSchema
from chatup_chat.core.admin import initiate_admin
from chatup_chat.core.loader import load_chat_bot
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.chat import Chat
from chatup_chat.core.customers import initiate_conversation

message_schema = AdminMessageSchema()
chat = Chat()
cache = RedisClusterJson()


class Admin(Namespace):

    def on_connect(self):
        print("Admin connected")

    def on_disconnect(self):
        print("Admin disconnected")

    def on_get_live_conversations(self, data):
        shop_id = data["shop_id"]
        conversation_ids = initiate_admin(shop_id)
        emit("init_response", conversation_ids)

    def on_message(self, data):
        print("Received another event with data: ", data)
        admin_message = message_schema.load(data)

    def on_leave_room(self, data):
        print("Received another event with data: ", data)
        admin_message = message_schema.load(data)
