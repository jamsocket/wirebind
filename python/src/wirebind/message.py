from typing import Any


class Message:
    def __init__(self, message: Any, channel: int):
        self.message = message
        self.channel = channel

    def to_dict(self):
        return {
            "message": self.message,
            "ch": self.channel,
        }

    @staticmethod
    def from_dict(data):
        return Message(
            data["message"],
            data["ch"],
        )

    def __repr__(self):
        return f"Message({self.message}, {self.channel})"
