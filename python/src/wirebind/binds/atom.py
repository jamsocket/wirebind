from typing import Any
from ..broadcast import BroadcastList
from ..sender import Sender, AbstractSender
from . import Packable

class Atom(Packable):
    value: Any
    listeners: BroadcastList

    def __init__(self, value: Any):
        self.value = value
        self.listeners = BroadcastList()

    def add_listener(self, sender: AbstractSender):
        self.listeners.add(sender)

    def set(self, value: Any):
        self.value = value
        self.listeners.send(value)

    def get(self) -> Any:
        return self.value

    @staticmethod
    def pack_type() -> str:
        return "atom"

    def bind(self, sender: AbstractSender):
        sender.send(self.value)
        self.add_listener(sender)

    def pack(self):
        getter = Sender(self.bind)
        setter = Sender(self.set)

        return {
            "type": self.pack_type(),
            "get": getter,
            "set": setter,
        }

    @staticmethod
    def from_packed(packed: dict):
        return AtomReplica(packed)


class AtomReplica:
    value: Any = None

    def update(self, value):
        self.value = value

    def __init__(self, packed: dict):
        packed["get"].send(Sender(self.update))
        self.setter = packed["set"]

    def set(self, value: Any):
        self.setter.send(value)
