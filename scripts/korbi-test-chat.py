from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage


def main():
    chat = ChatOpenAI(
        openai_organization="org-YnH8ww77r1MiI2RcFE0jvT3Y",
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
        temperature=0,
    )

    conversation = ConversationChain(llm=chat, verbose=True, memory=ConversationBufferMemory())

    print("Hello, I am ChatGPT CLI!")

    while True:
        user_input = input("> ")

        ai_response = conversation.predict(input=user_input)

        print("\nAssistant:\n", ai_response, "\n")


if __name__ == "__main__":
    main()
