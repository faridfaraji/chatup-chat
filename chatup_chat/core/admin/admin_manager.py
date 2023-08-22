

from typing import List
from chatup_chat.core.admin.admin import Admin
from chatup_chat.core.cache import RedisClusterJson
from chatup_chat.core.exceptions import AdminFoundError
cache = RedisClusterJson()


class AdminManager:

    @classmethod
    def init_admin(cls, shop_id: str, session_id: str) -> Admin:
        try:
            admin = cls.get_admin(shop_id)
            admin.session_id = session_id
        except AdminFoundError:
            admin = Admin(session_id=session_id, shop_id=shop_id)
        cls.remove_admin(admin)
        cls.set_admin(admin)
        return admin

    @classmethod
    def get_admin(cls, shop_id: str) -> Admin:
        admins = cache.get_by_patterns(f"admin_{shop_id}")
        admins: List[Admin] = [Admin(**admin) for admin in admins]
        if len(admins) > 1:
            raise AdminFoundError("More than one admin found")
        elif len(admins) == 0:
            raise AdminFoundError("Admin not found")
        return admins[0]

    @classmethod
    def get_admin_by_session(cls, session_id: str) -> Admin:
        admins = cache.get_by_patterns(f"admin_*{session_id}")
        admins: List[Admin] = [Admin(**admin) for admin in admins]
        if len(admins) > 1:
            raise AdminFoundError("More than one admin found")
        elif len(admins) == 0:
            raise AdminFoundError("Admin not found")
        return admins[0]

    @classmethod
    def set_admin(cls, admin: Admin):
        cache[f"admin_{admin.shop_id}_{admin.session_id}"] = admin.to_dict()

    @classmethod
    def get_space_admin(cls, space_id) -> Admin:
        admins = cache.get_by_patterns(f"admin_{space_id}_*")
        if len(admins) > 1:
            raise AdminFoundError("More than one admin found")
        elif len(admins) == 0:
            raise AdminFoundError("Admin not found")
        return Admin(**admins[0])

    @classmethod
    def checkout_admin(cls, session_id: str):
        cache.clear_cache(f"admin_*_{session_id}")

    @classmethod
    def reset_connections(cls):
        admins = cls.get_space_admin("admin_*")
        for admin in admins:
            admin.notify_admin_of_off_room()

    @classmethod
    def remove_admin(cls, admin: Admin):
        cache.clear_cache(f"admin_{admin.shop_id}")
