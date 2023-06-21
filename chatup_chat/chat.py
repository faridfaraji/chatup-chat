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

from chatup_chat.core.open_ai_client import get_user_query_embedding

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

db_client = DatabaseApiClient()


class ChatUpStreamHandler(StreamingStdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs: Any):
        emit("ai_response", token)


def create_conversation_chain():
    chat = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k",
        streaming=True,
        callbacks=[ChatUpStreamHandler()],
        temperature=0
    )
    template = """The following is a friendly conversation between a human and an AI customer Assistant.
    the context helps the AI to answer the customer's question. The AI is not talkative and provides specific answers.
    If the AI does not know the answer to a question based on the context provided, it truthfully says it does not know and provides the
    store contact info and asks them to contact them. While the AI answers the customers questions based on the contexts provided 
    the AI does not mention the word context or let the customer know where it is getting his knowledge from
    {history}
    Current conversation:
    {input}
    AI Assistant:"""

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
    memory = ConversationBufferMemory(input_key="input")
    return ConversationChain(prompt=PROMPT, llm=chat, verbose=True, memory=memory)


conversations = {}


@socketio.on("connect")
def handle_connect():
    conversations[request.sid] = {"conversation_chain": None}
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
        conv_chain = conversations[request.sid]["conversation_chain"]
        if conv_chain is None:
            conversations[request.sid]["conversation_chain"] = create_conversation_chain()
        query_embedding = get_user_query_embedding(user_input)
        context = db_client.get_closest_shop_doc(query_embedding, shop_id)
        input = f"""\nContext:{context}\nCustomer: {user_input}"""
        user_input = input
        conversations[request.sid]["conversation_chain"].predict(input=user_input)
    else:
        print(f"Error: No conversation found for {request.sid}")


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8014)
