from chatup_chat.adapter.db_client import DatabaseApiClient
from shopify import session_token
from flask import request
import os
import logging
from urllib.parse import unquote, urlparse
from flask_socketio import disconnect

from dotenv import load_dotenv
load_dotenv()

SHOPIFY_SECRET = os.environ.get('SHOPIFY_SECRET')
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')

db_client = DatabaseApiClient()
api_keys = SHOPIFY_API_KEY.split(",")
secrets = SHOPIFY_SECRET.split(",")


def validate_shopify_token():
    for api_key, secret in zip(api_keys, secrets):
        try:
            decoded_session_token = session_token.decode_from_header(
                authorization_header=request.headers.get("Authorization", ""),
                api_key=api_key,
                secret=secret,
            )
            shop_domain = decoded_session_token.get("dest")
            decoded_url = unquote(shop_domain)
            shop_domain = urlparse(decoded_url).netloc
            shop = db_client.get_shop_profile_by_shop_url(shop_domain)
            shop_id = shop["shop_identifier"]
            return shop_id
        except session_token.SessionTokenError:
            # Log the error here
            logging.exception('ERROR')
            print("Could not authenticate the session token")
            disconnect()
            raise Exception()


def authorize_admin(admin_manager):
    shop_id = validate_shopify_token()
    admin = admin_manager.init_admin(shop_id, request.sid)
    return admin
