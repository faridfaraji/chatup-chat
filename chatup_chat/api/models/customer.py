
from marshmallow import Schema, fields


class CustomerSchema(Schema):
    shop_id = fields.Int(required=True)
    conversation_id = fields.Str(missing="")


class MessageSchema(Schema):
    conversation_id = fields.Str(required=True)
    message = fields.Str(message="")
