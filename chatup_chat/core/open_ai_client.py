from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()


def get_user_query_embedding(query):
    return embeddings.embed_documents([query])[0]
