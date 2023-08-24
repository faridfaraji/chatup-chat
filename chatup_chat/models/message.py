

from dataclasses import dataclass


@dataclass
class Message:
    message: str
    message_type: str
    metadata: list = None

    def to_dict(self):
        if self.metadata is None:
            self.metadata = []
        return {
            "message": self.message,
            "message_type": self.message_type,
            "metadata": self.metadata
        }

    @classmethod
    def make_obj(cls, message_data: dict):
        return Message(message_data["message"], message_data["message_type"], message_data["metadata"])
