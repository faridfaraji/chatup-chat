from langchain.embeddings.openai import OpenAIEmbeddings
import openai

from chatup_chat.core import Bot


embeddings = OpenAIEmbeddings()


def get_user_query_embedding(query):
    return embeddings.embed_documents([query])[0]


MODEL_NAME = "gpt-3.5-turbo-16k"


def chat_completion(bot: Bot, stream=True):
    messages = bot.memory.get_messages()
    print(messages)
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
                if bot.response is None:
                    bot.response = []
                bot.response.append(message.choices[0].delta.content)
                result.append(message.choices[0].delta.content)
    else:
        if bot.response is None:
            bot.response = []
        bot.response.append(completion.choices[0].message.content)
        result.append(completion.choices[0].message.content)
    bot.is_response_finished = True
    response = "".join(result).strip()
    print(response)
    return response

