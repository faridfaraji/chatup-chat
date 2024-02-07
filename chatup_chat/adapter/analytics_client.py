

import asyncio
import aiohttp
from chatup_chat.config import config


class ChatAnalyticsApiClient:
    def __init__(self):
        self.config = config
        self.analytics_base_url = self.config.chat_analytics.url_api_version

    def _gen_url(self, route):
        return f"{self.analytics_base_url}/{route}"

    def _make_request(self, method, route, **kwargs):
        response = method(self._gen_url(route), **kwargs)
        response.raise_for_status()
        return response.json()

    async def _make_async_request(self, method, route, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(self._gen_url(route), **kwargs):
                pass

    def submit_conversation_analytics(self, conversation_id):
        asyncio.run(self._make_async_request("post", f"conversations/{conversation_id}/analyze"))
