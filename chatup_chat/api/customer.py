from flask_socketio import Namespace, emit
from chatup_chat.api.models.customer import CustomerSchema, MessageSchema
from chatup_chat.core.customers import initiate_conversation, respond_customer_message

customer_schema = CustomerSchema()
message_schema = MessageSchema()


class Customer(Namespace):

    def on_connect(self):
        print("Customer connected")

    def on_disconnect(self):
        print("Customer disconnected")

    def on_init(self, data):
        customer = customer_schema.load(data)
        conversation_id = initiate_conversation(customer)
        emit("init_response", conversation_id)

    def on_message(self, data):
        print("Received another event with data: ", data)
        customer_message = message_schema.load(data)
        respond_customer_message(customer_message)
        # emit("ai_response", {"data": "This is another response"})
