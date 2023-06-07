
import requests
from chatup_chat.config import config


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

    def get_shop_description_by_id(self, shop_id):
        return self._make_request(requests.get, f"shops/{shop_id}")["description"]
