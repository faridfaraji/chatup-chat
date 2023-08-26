from __future__ import annotations

from flask_socketio import Namespace, emit
from chatup_chat.api.models.customer import CustomerSchema, MessageSchema
from chatup_chat.core.admin.admin_manager import AdminManager
from chatup_chat.core.loader import load_chat_bot
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.customers import initiate_conversation
from flask import request
from chatup_chat.core.message_enums import MessageType

from chatup_chat.core.room.room_manager import RoomManager
from chatup_chat.models.message import Message

customer_schema = CustomerSchema()
message_schema = MessageSchema()
cache = RedisClusterJson()

room_manager = RoomManager()
admin_manager = AdminManager()

room_manager.admin_manager = admin_manager
admin_manager.room_manager = room_manager


class Customer(Namespace):

    def on_connect(self):
        print("Customer connected")

    def on_disconnect(self):
        room_manager.checkout_rooms(request.sid)
        print("Customer disconnected")

    def on_init(self, data):
        customer = customer_schema.load(data)
        conversation_id = initiate_conversation(room_manager, customer)
        emit("init_response", conversation_id)

    def on_message(self, data):
        print("Received another event with data: ", data)
        room = room_manager.get_room_by_session(request.sid)
        customer_message = message_schema.load(data)
        customer_bot = load_chat_bot(conversation_id=customer_message["conversation_id"])
        customer_bot.add_context(customer_message["message"])
        room.set_bot(customer_bot)
        room.user_says(
            Message(
                message=customer_message["message"],
                message_type=MessageType.USER.value,
                metadata=["customer"]
            )
        )

    def on_request_human(self, data):
        print("Received another event with data: ", data)
        customer_message = message_schema.load(data)
