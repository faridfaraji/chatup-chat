
import asyncio
from typing import List
import aiohttp
import requests
from chatup_chat.config import config
from funcy import print_durations


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

    def get_prompt(self):
        return self._make_request(requests.get, "prompt")["prompt"]

    def get_shop_temperature(self, shop_id: int):
        return self._make_request(requests.get, f"shops/{shop_id}")["bot_temperature"]

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

    def add_message(self, conversation_id, message, message_type):
        data = {
            "message_type": message_type,
            "message": message
        }
        asyncio.run(self._make_async_request("post", f"conversations/{conversation_id}/messages", json=data))

    def get_conversation(self, conversation_id):
        return self._make_request(requests.get, f"conversations/{conversation_id}")

    def add_conversation(self, shop_id):
        data = {
            "shop_id": shop_id,
            "messages": []
        }
        return self._make_request(requests.post, "conversations", json=data)
