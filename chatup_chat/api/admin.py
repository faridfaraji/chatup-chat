from __future__ import annotations
from flask import request

from flask_socketio import Namespace, emit
from chatup_chat.api.models.customer import AdminMessageSchema, CustomerSchema, MessageSchema
from chatup_chat.api.util import authorize_admin
from chatup_chat.core.admin import AdminManager
from chatup_chat.core.loader import load_chat_bot
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.chat import Chat
from chatup_chat.core.customers import initiate_conversation
from chatup_chat.core.room import RoomManager

message_schema = AdminMessageSchema()
chat = Chat()
cache = RedisClusterJson()


class Admin(Namespace):

    def on_connect(self):
        admin = authorize_admin()
        print("Admin connected")
        rooms = RoomManager.get_live_rooms(admin.shop_id)
        conversation_ids = [room.conversation_id for room in rooms]

        emit("live_conversations", conversation_ids)

    def on_disconnect(self):
        AdminManager.checkout_admin(request.sid)
        print("Admin disconnected")

    def on_get_live_conversations(self):
        admin = AdminManager.get_admin(request.sid)
        rooms = RoomManager.get_live_rooms(admin.shop_id)
        conversation_ids = [room.conversation_id for room in rooms]
        emit("live_conversations", conversation_ids)

    def on_message(self, data):
        print("Received another event with data: ", data)
        admin_message = message_schema.load(data)

