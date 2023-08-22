from __future__ import annotations
from flask import request

from flask_socketio import Namespace, emit
from chatup_chat.api.models.customer import AdminMessageSchema
from chatup_chat.api.util import authorize_admin
from chatup_chat.core.admin.admin_manager import AdminManager
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.chat import Chat
from chatup_chat.core.loader import load_chat_bot
from chatup_chat.core.room.room_manager import RoomManager

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
        admin = AdminManager.get_admin_by_session(request.sid)
        rooms = RoomManager.get_live_rooms(admin.shop_id)
        conversation_ids = [room.conversation_id for room in rooms]
        emit("live_conversations", conversation_ids)

    def on_message(self, data):
        admin_message = message_schema.load(data)
        customer_bot = load_chat_bot(conversation_id=admin_message["conversation_id"])
        admin = AdminManager.get_admin_by_session(request.sid)
        print("Received another event with data: ", data)
        room = RoomManager.get_room_by_conversation_id(admin_message["conversation_id"])
        room.set_bot(customer_bot)
        admin.take_over_conversation(room)
        admin.message_user(room, admin_message["message"])
