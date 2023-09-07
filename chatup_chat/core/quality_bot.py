

from attr import define, field
from chatup_chat.adapter.open_ai_client import chat_completion
from chatup_chat.core import Bot


@define
class QualityBot(Bot):
    model_name: str = field(default="gpt-4", kw_only=True)

    def check_quality(self, response: str, bot: Bot):
        if not self.is_speaking:
            return
        quality_check_message = {
            "role": "user",
            "content": f"You are a customer support quality check, your responsibility is to correct and improve the response given by the customer assistant " \
            "based on some document that is provided to you. We want to make sure the customer assistant's response is not contradicting the document's information or " \
            " things that are not supported by the document. " \
            f"{bot.memory.context_question}. " \
            f"And the customer support responded with: ```{response}.``` " \
            f"Now Given this document here: ```{bot.memory.context}``` " \
            "You must follow these rules in your response: " \
            "1. just only return what you would have said to the customer and nothing else. 2. It is very important that your response not be longer than customer assistant's ."
        }
        self.memory.add_message(quality_check_message)
        result = chat_completion(self, stream=True)
        print("REPHRASE: ", result)
        return result


@define
class CategoryBot(Bot):
    category: str = field(default="", kw_only=True)

    def check_category(self, bot: Bot):
        quality_check_message = {
            "role": "user",
            "content": f"{bot.memory.context_question} " \
            "Categorize the user's message as one of the following: [ Products, Order, Payment, Services, Policies, Complaint, General, Other ] " \
            "in your response just say ONLY ONE of the categories in one word, it is very important to be from one of those categories mentioned."
        }
        self.memory.add_message(quality_check_message)
        result = chat_completion(self, stream=False)
        print("CATEGORY: ", result)
        bot.speak()
        self.category = result


class LatestInquiryBot(Bot):

    def check_inquiry(self, bot: Bot):
        messages = [{"message": msg["message"], "role": msg["message_type"]} for msg in bot.memory.messages]
        quality_check_message = {
            "role": "user",
            "content": f"Here is a conversation between a user and a customer support: '''{messages}'''. " \
            "give me a clear and concise short summary of what the latest user inquiry is about."
        }
        self.memory.add_message(quality_check_message)
        result = chat_completion(self, stream=False)
        print("USER INQUIRY: ", result)
        bot.memory.set_context_question(result)
