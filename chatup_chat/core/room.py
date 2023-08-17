from dataclasses import dataclass
from typing import List
from chatup_chat.core.cache import RedisClusterJson

from flask_socketio import join_room, leave_room, send, emit


cache = RedisClusterJson()


@dataclass
class Room:
    id: str = None
    is_live: bool = False
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
            )
        return room

    @classmethod
    def occupy_room(cls, room: Room):
        room.is_live = True
        cache[room.id] = room.to_dict()

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
        print(rooms)
        rooms: List[Room] = [Room(**room) for room in rooms]
        print("-->", rooms)
        for room in rooms:
            print(room)
            room.is_live = False
            cache[room.id] = room.to_dict()

    @classmethod
    def update_room(cls, room: Room):
        cache[room.id] = room.to_dict()

    @classmethod
    def get_room_id(cls, space, unique_id):
        return f"room_{space}:{unique_id}"
