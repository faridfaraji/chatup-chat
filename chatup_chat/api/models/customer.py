
from marshmallow import Schema, fields


class CustomerSchema(Schema):
    shop_id = fields.Int(required=True)
    conversation_id = fields.Str(missing="", allow_none=True)
    metadata = fields.Dict(missing={}, allow_none=True)


class MessageSchema(Schema):
    conversation_id = fields.Str(required=True)
    message = fields.Str(message="")


class AdminMessageSchema(Schema):
    conversation_id = fields.Str(required=True)
    message = fields.Str(message="")
