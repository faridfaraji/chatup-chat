

from langchain import ConversationChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory

from chatup_chat.core.response_handler import ChatUpStreamHandler


def create_conversation_chain():
    chat = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k",
        streaming=True,
        callbacks=[ChatUpStreamHandler()],
        temperature=0
    )
    template = """The following is a friendly conversation between a human and an AI customer Assistant.
the context helps the AI to answer the customer's question. It is very important that the The AI is not talkative and 
provides short answers. If the AI does not know the answer to a question based on the context provided. it truthfully says it
does not know and provides the store contact info and asks them to contact them. While the AI answers
the customers questions based on the contexts provided the AI does not mention the word context or
let the customer know where it is getting his knowledge from. The context provided does not necessarily
relate to the question being asked if its not related refer them to the store contact info. The AI
only gives responses that satisfy the question and not extra unecessary information from the context or anywhere else.
The AI response is very important to be always in html format. the ai response needs to be well formatted with any necessary
indenations like new lines (<br>) and such.
{history}
Current conversation:
Customer: {input}
AI Assistant:"""

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
    memory = ConversationSummaryBufferMemory(
        llm=chat, input_key="input", max_token_limit=10000, human_prefix="Customer"
    )
    return ConversationChain(prompt=PROMPT, llm=chat, verbose=True, memory=memory)
