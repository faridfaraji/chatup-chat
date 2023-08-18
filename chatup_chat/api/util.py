from chatup_chat.adapter.db_client import DatabaseApiClient
from shopify import session_token
from flask import request
import shopify
import os
import logging
from urllib.parse import unquote, urlparse
from flask_socketio import disconnect

from chatup_chat.core.admin import AdminManager

db_client = DatabaseApiClient()

def validate_shopify_token():
    try:
        decoded_session_token = session_token.decode_from_header(
            authorization_header=request.headers.get("Authorization", ""),
            api_key=os.environ.get("SHOPIFY_API_KEY"),
            secret=os.environ.get("SHOPIFY_API_SECRET"),
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


# def validate_session_token(func):
#     def wrapper(*args, **kwargs):
#         try:
#             print('==>', request.method, os.environ.get("SHOPIFY_API_KEY"), os.environ.get("SHOPIFY_API_SECRET"))
#             decoded_session_token = session_token.decode_from_header(
#                 authorization_header=request.headers.get("Authorization", ""),
#                 api_key=os.environ.get("SHOPIFY_API_KEY"),
#                 secret=os.environ.get("SHOPIFY_API_SECRET"),
#             )
#             shop_domain = decoded_session_token.get("dest")
#             decoded_url = unquote(shop_domain)
#             shop_domain = urlparse(decoded_url).netloc
#             shop = db_client.get_shop_profile_by_shop_url(shop_domain)
#             shop_id = shop["shop_identifier"]
#             AdminManager.init_admin(shop_id, request.sid)
#             return func(*args)
#         except session_token.SessionTokenError:
#             # Log the error here
#             logging.exception('ERROR')
#             print("Could not authenticate the session token")
#             disconnect()
#         except Exception:
#             logging.exception('ERROR')
#             print("Exception occurred while validating the session token")
#     return wrapper


def authorize_admin():
    shop_id = validate_shopify_token()
    admin = AdminManager.init_admin(shop_id, request.sid)
    return admin
