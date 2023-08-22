from langchain.embeddings.openai import OpenAIEmbeddings
import openai

from chatup_chat.core import Bot
from chatup_chat.core.room.room import Room


embeddings = OpenAIEmbeddings()


def get_user_query_embedding(query):
    return embeddings.embed_documents([query])[0]


MODEL_NAME = "gpt-3.5-turbo-16k"


def chat_completion(room: Room, stream=True):
    bot = room.bot
    messages = bot.memory.get_messages()
    print(messages)
    print(bot.bot_temperature)
    completion = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=messages,
        stream=stream,
        temperature=bot.bot_temperature
    )
    result = []
    if stream:
        for message in completion:
            delta = message.choices[0].delta
            if delta.get("content"):
                room.ai_token_call_back(message.choices[0].delta.content)
                result.append(message.choices[0].delta.content)
    else:
        room.ai_token_call_back(completion.choices[0].message.content)
        result.append(completion.choices[0].message.content)

    room.ai_feedback_finished()
    return "".join(result).strip()
