from langchain.embeddings.openai import OpenAIEmbeddings
import openai

from chatup_chat.core import Bot


embeddings = OpenAIEmbeddings()


def get_user_query_embedding(query):
    return embeddings.embed_documents([query])[0]


MODEL_NAME = "gpt-3.5-turbo-16k"


def chat_completion(bot: Bot, stream=True):
    messages = bot.memory.get_messages()
    print("============================")
    print(messages)
    print("============================")
    completion = openai.ChatCompletion.create(
        model=bot.model_name,
        messages=messages,
        stream=stream,
        temperature=bot.bot_temperature
    )
    result = []
    if stream:
        for message in completion:
            delta = message.choices[0].delta
            if delta.get("content"):
                bot.response_handler(message.choices[0].delta.content)
                result.append(message.choices[0].delta.content)
    else:
        bot.response_handler(completion.choices[0].message.content)
        result.append(completion.choices[0].message.content)
    response = "".join(result).strip()
    return response
