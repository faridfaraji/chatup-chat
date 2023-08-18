

from dataclasses import dataclass
from typing import List
from chatup_chat.core.cache import RedisClusterJson
from flask_socketio import Namespace, emit

from flask import request
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


class AdminManager:

    @classmethod
    def init_admin(cls, shop_id: str, session_id: str) -> Admin:
        admin = Admin(session_id=session_id, shop_id=shop_id)
        cls.set_admin(admin)
        return admin

    @classmethod
    def get_admin(cls, session_id: str):
        admin_data = cache[f"admin_{session_id}"]
        if admin_data:
            return Admin(**admin_data)
        return None

    @classmethod
    def set_admin(cls, admin: Admin):
        cache[f"admin_{admin.shop_id}_{admin.session_id}"] = admin.to_dict()

    @classmethod
    def get_space_admin(cls, space_id):
        admins = cache.get_by_patterns(f"admin_{space_id}_*")
        return [Admin(**admin) for admin in admins]

    @classmethod
    def checkout_admin(cls, session_id: str):
        cache.clear_cache(f"admin_*_{session_id}")

    @classmethod
    def reset_connections(cls):
        admins = cls.get_space_admin("admin_*")
        for admin in admins:
            admin.notify_admin_of_off_room()

# def process_admin_msg(shop_id, conversation_id, msg):
#     room = RoomManager.get_room(shop_id, conversation_id)
#     room.admin_managed = True
#     room.admin_msg()
