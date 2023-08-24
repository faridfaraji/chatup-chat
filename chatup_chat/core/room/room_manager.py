
from typing import List
from chatup_chat.core import Manager
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.exceptions import AdminFoundError, RoomFoundError
from chatup_chat.core.room.room import Room


cache = RedisClusterJson()


class RoomManager(Manager):
    def __init__(self, admin_manager: Manager = None):
        self.admin_manager = admin_manager

    def get_room(self, shop_id, session_id, unique_id) -> Room:
        try:
            room = self.get_room_by_conversation_id(unique_id)
            room.space_id = shop_id
            room.occupant_session_id = session_id
        except RoomFoundError:
            room = Room(
                space_id=shop_id,
                occupant_session_id=session_id,
                conversation_id=unique_id
            )
        self.remove_room(room)
        self.set_room(room)
        return room

    def get_room_by_session(self, session_id) -> Room:
        rooms = cache.get_by_patterns(f"room_*:{session_id}:")
        rooms: List[Room] = [Room(**room) for room in rooms]
        if len(rooms) > 1:
            raise RoomFoundError("More than One room found")
        if len(rooms) == 0:
            raise RoomFoundError("Room not found")
        return rooms[0]

    def get_room_by_conversation_id(self, convo_id) -> Room:
        rooms = cache.get_by_patterns(f"room_*:{convo_id}")
        rooms: List[Room] = [Room(**room) for room in rooms]
        if len(rooms) > 1:
            raise RoomFoundError("More than One room found")
        if len(rooms) == 0:
            raise RoomFoundError("Room not found")
        return rooms[0]

    def occupy_room(self, room: Room):
        room.is_live = True
        self.set_room(room)
        try:
            admin = self.admin_manager.get_space_admin(room.space_id)
            admin.notify_admin_of_live_room(room.conversation_id)
        except AdminFoundError:
            pass

    def get_live_rooms(self, space) -> List[Room]:
        rooms = cache.get_by_patterns(f"room_{space}")
        rooms: List[Room] = [Room(**room) for room in rooms]
        live_rooms = [room for room in rooms if room.is_live]
        return live_rooms

    def checkout_rooms(self, session_id: str):
        room = self.get_room_by_session(session_id)
        room.is_live = False
        try:
            admin = self.admin_manager.get_space_admin(room.space_id)
            admin.notify_admin_of_off_room(room.conversation_id)
        except AdminFoundError:
            pass
        self.set_room(room)

    def set_room(self, room: Room):
        room.save()

    def remove_room(self, room: Room):
        cache.clear_cache(f"room_*:{room.conversation_id}")
