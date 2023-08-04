from langchain.embeddings.openai import OpenAIEmbeddings
import openai

from chatup_chat.core import Bot


embeddings = OpenAIEmbeddings()


def get_user_query_embedding(query):
    return embeddings.embed_documents([query])[0]


MODEL_NAME = "gpt-3.5-turbo-16k"


def chat_completion(bot: Bot, call_back_handler, stream=True):
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
                call_back_handler.on_llm_new_token(message.choices[0].delta.content)
                result.append(message.choices[0].delta.content)
    else:
        call_back_handler.on_llm_new_token(completion.choices[0].message.content)
        result.append(completion.choices[0].message.content)

    return "".join(result).strip()
