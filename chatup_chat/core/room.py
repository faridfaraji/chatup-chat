from dataclasses import dataclass
from typing import List
from chatup_chat.core.admin import AdminManager
from chatup_chat.core.cache import RedisClusterJson

from flask_socketio import emit


cache = RedisClusterJson()


@dataclass
class Room:
    id: str = None
    is_live: bool = False
    space_id: str = None
    admin_managed: bool = False
    conversation_id: str = None
    admin_session_id: str = None
    occupant_session_id: str = None

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

    def admin_msg(self, msg):
        emit("admin_response", msg, to=self.occupant_session_id)


class RoomManager:

    @classmethod
    def get_room(cls, shop_id, session_id) -> Room:
        room_data = cache[cls.get_room_id(shop_id, session_id)]
        if room_data:
            room = Room(**room_data)
        else:
            room = Room(
                id=cls.get_room_id(shop_id, session_id),
                space_id=shop_id
            )
        return room

    @classmethod
    def occupy_room(cls, room: Room):
        room.is_live = True
        cache[room.id] = room.to_dict()
        admins = AdminManager.get_space_admin(room.space_id)
        print('--->', admins)
        for admin in admins:
            admin.notify_admin_of_live_room(room.conversation_id)

    @classmethod
    def get_live_rooms(cls, space) -> List[Room]:
        rooms = cache.get_by_patterns(f"room_{space}")
        print(rooms)
        rooms: List[Room] = [Room(**room) for room in rooms]
        live_rooms = [room for room in rooms if room.is_live]
        return live_rooms

    @classmethod
    def checkout_rooms(cls, session_id: str):
        rooms = cache.get_by_patterns(f"room_*:{session_id}")
        rooms: List[Room] = [Room(**room) for room in rooms]
        for room in rooms:
            print(room)
            room.is_live = False
            admins = AdminManager.get_space_admin(room.space_id)
            cache[room.id] = room.to_dict()
            for admin in admins:
                admin.notify_admin_of_off_room(room.conversation_id)

    @classmethod
    def update_room(cls, room: Room):
        cache[room.id] = room.to_dict()

    @classmethod
    def get_room_id(cls, space, unique_id):
        return f"room_{space}:{unique_id}"
