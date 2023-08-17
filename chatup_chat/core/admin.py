

from typing import List

from chatup_chat.core.room import Room, RoomManager
from flask import request


def initiate_admin(shop_id: str) -> List[str]:
    rooms: List[Room] = RoomManager.get_live_rooms(shop_id)
    for room in rooms:
        room.admin_session_id = request.sid
        RoomManager.update_room(room)
    return [room.conversation_id for room in rooms]


def process_admin_msg(shop_id, conversation_id, msg):
    room = RoomManager.get_room(shop_id, conversation_id)
    room.admin_managed = True
    room.admin_msg()
