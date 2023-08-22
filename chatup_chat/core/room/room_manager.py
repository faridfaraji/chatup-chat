
from typing import List
from chatup_chat.core.admin.admin_manager import AdminManager
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.exceptions import AdminFoundError, RoomFoundError
from chatup_chat.core.room.room import Room


cache = RedisClusterJson()


class RoomManager:

    @classmethod
    def get_room(cls, shop_id, session_id, unique_id) -> Room:
        try:
            room = cls.get_room_by_conversation_id(unique_id)
            room.space_id = shop_id
            room.occupant_session_id = session_id
        except RoomFoundError:
            room = Room(
                space_id=shop_id,
                occupant_session_id=session_id,
                conversation_id=unique_id
            )
        cls.remove_room(room)
        cls.set_room(room)
        return room

    @classmethod
    def get_room_by_session(cls, session_id) -> Room:
        rooms = cache.get_by_patterns(f"room_*:{session_id}:")
        rooms: List[Room] = [Room(**room) for room in rooms]
        if len(rooms) > 1:
            raise RoomFoundError("More than One room found")
        if len(rooms) == 0:
            raise RoomFoundError("Room not found")
        return rooms[0]

    @classmethod
    def get_room_by_conversation_id(cls, convo_id) -> Room:
        rooms = cache.get_by_patterns(f"room_*:{convo_id}")
        rooms: List[Room] = [Room(**room) for room in rooms]
        if len(rooms) > 1:
            raise RoomFoundError("More than One room found")
        if len(rooms) == 0:
            raise RoomFoundError("Room not found")
        return rooms[0]

    @classmethod
    def occupy_room(cls, room: Room):
        room.is_live = True
        cls.set_room(room)
        try:
            admin = AdminManager.get_space_admin(room.space_id)
            admin.notify_admin_of_live_room(room.conversation_id)
        except AdminFoundError:
            pass

    @classmethod
    def get_live_rooms(cls, space) -> List[Room]:
        rooms = cache.get_by_patterns(f"room_{space}")
        rooms: List[Room] = [Room(**room) for room in rooms]
        live_rooms = [room for room in rooms if room.is_live]
        return live_rooms

    @classmethod
    def checkout_rooms(cls, session_id: str):
        room = cls.get_room_by_session(session_id)
        room.is_live = False
        try:
            admin = AdminManager.get_space_admin(room.space_id)
            admin.notify_admin_of_off_room(room.conversation_id)
        except AdminFoundError:
            pass
        cls.set_room(room)

    @classmethod
    def set_room(cls, room: Room):
        room.save()

    @classmethod
    def remove_room(cls, room: Room):
        cache.clear_cache(f"room_*:{room.conversation_id}")
