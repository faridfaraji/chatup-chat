import json

from flask import Flask, request
from chatup_chat.core.db_client import DatabaseApiClient
from flask_socketio import SocketIO, emit
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
from typing import Any

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

db_client = DatabaseApiClient()


class ChatUpStreamHandler(StreamingStdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs: Any):
        emit("ai_response", token)


def create_conversation_chain():
    chat = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callbacks=[ChatUpStreamHandler()],
        temperature=0,
    )
    template = """The following is a friendly conversation between a customer and an AI customer assistant. The AI is helpfull and descriptive. The AI should only talk about things relating to the products or the questions being asked. Respond with answeres as short as possible.
    Current conversation:
    {history}
    {input}
    AI Assistant:"""

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
    memory = ConversationBufferMemory(input_key="input")
    return ConversationChain(prompt=PROMPT, llm=chat, verbose=True, memory=memory)


conversations = {}


@socketio.on("connect")
def handle_connect():
    conversations[request.sid] = {"chain": create_conversation_chain(), "first_message": True}
    print(f"New connection: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in conversations:
        del conversations[request.sid]
    print(f"Disconnected: {request.sid}")


@socketio.on("user_message")
def handle_user_message(data):
    print(data)
    user_input = data["message"]
    shop_id = int(data["shop_id"])
    print(user_input)
    if request.sid in conversations:
        first_message = conversations[request.sid]["first_message"]

        if first_message:
            conversations[request.sid]["first_message"] = False
            business = db_client.get_shop_description_by_id(shop_id)
            input = f"""Given the shop description: {business}\nHuman: {user_input}"""
            user_input = input
        else:
            user_input = f"\tHuman: {user_input}"

        conversations[request.sid]["chain"].predict(input=user_input)
    else:
        print(f"Error: No conversation found for {request.sid}")


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8014)
