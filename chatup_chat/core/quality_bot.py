

import threading
from chatup_chat.adapter.open_ai_client import chat_completion
from chatup_chat.core import Bot


class QualityBot(Bot):

    def check_quality(self, response: str, bot: Bot):
        quality_check_message = {
            "role": "user",
            "content": f"The user said to the customer support : ```{bot.memory.context_question}```. " \
            f"And the customer support responds with: ```{response}.``` " \
            f"Given this information here: ```{bot.memory.context}``` " \
            "Either correct the customer support's response or return: I dont have enough information to answer this please contact us directly"
        }
        self.memory.add_message(quality_check_message)
        result = chat_completion(self, stream=True)
        return result


class CategoryBot(Bot):

    def check_category(self, bot: Bot):
        quality_check_message = {
            "role": "user",
            "content": f"The user said to the customer support : '''{bot.memory.context_question}'''. " \
            "Categorize the user's message as one of the following: Products, Services, Policies, Complaint, General, Other. " \
            "in your response just say only one of the categories in one word."
        }
        self.memory.add_message(quality_check_message)
        result = chat_completion(self, stream=False)
        if "GENERAL" in result.upper() or "OTHER" in result.upper():
            bot.speak()
        else:
            bot.quality_bot.speak()


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
        bot.memory.set_context_question(result)
