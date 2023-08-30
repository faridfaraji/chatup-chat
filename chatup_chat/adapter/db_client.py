
import asyncio
from typing import List
import aiohttp
import requests
from chatup_chat.config import config
from funcy import print_durations

from chatup_chat.models.message import Message


class DatabaseApiClient:
    def __init__(self):
        self.config = config
        self.db_base_url = self.config.database.url_api_version

    def _gen_url(self, route):
        return f"{self.db_base_url}/{route}"

    def _make_request(self, method, route, **kwargs):
        response = method(self._gen_url(route), **kwargs)
        response.raise_for_status()
        return response.json()

    async def _make_async_request(self, method, route, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(self._gen_url(route), **kwargs):
                pass

    def get_negative_keywords(self, shop_id: int):
        return self._make_request(requests.get, f"shops/{shop_id}/negative-keywords")

    def get_prompt(self):
        return self._make_request(requests.get, "prompt")["prompt"]

    def get_shop_temperature(self, shop_id: int):
        return self._make_request(requests.get, f"shops/{shop_id}")["bot_temperature"]

    def get_shop_profile_by_shop_url(self, shop_url: str):
        shops = self._make_request(requests.get, "shops", params={"shop_url": shop_url})
        if shops:
            return shops[0]
        else:
            raise Exception("Shop not found")

    @print_durations
    def get_closest_shop_doc(self, embedding: List[float], shop_id: int):
        data = {
            "query_embedding": embedding,
            "number_of_docs": 7
        }
        docs = self._make_request(requests.post, f"shops/{shop_id}/closest-doc", json=data)
        context_doc = ""
        for doc in docs[:7]:
            context_doc += doc["document"]
        return context_doc

    def add_message(self, conversation_id, message: Message):
        data = message.to_dict()
        asyncio.run(self._make_async_request("post", f"conversations/{conversation_id}/messages", json=data))

    def get_conversation(self, conversation_id):
        return self._make_request(requests.get, f"conversations/{conversation_id}")

    def add_conversation(self, shop_id):
        data = {
            "shop_id": shop_id,
            "messages": [],
            "metadata": {}
        }
        return self._make_request(requests.post, "conversations", json=data)

    def get_messages(self, conversation_id):
        messages = self._make_request(requests.get, f"conversations/{conversation_id}/messages")
        messages = [Message.make_obj(msg) for msg in messages]
        return messages
