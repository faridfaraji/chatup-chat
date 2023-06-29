
from marshmallow import Schema, fields


class Customer(Schema):
    shop_id = fields.Int(required=True)
    conversation_id = fields.Str(missing="")


class Message(Schema):
    conversation_id = fields.Str(required=True)
    message = fields.Str(message="")
