from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .multiplex import Multiplexer


class AbstractSender(ABC):
    @abstractmethod
    def send(self, message: Any):
        pass

    def on_destroy(self, callback: Callable[[], None]):
        pass

    def destroy(self):
        pass


class Sender(AbstractSender):
    def __init__(self, callback: Callable[[Any], None]):
        self.callback = callback

    def send(self, message: Any):
        self.callback(message)


class RemoteSender(Sender):
    destroy_callbacks: list[Callable[[], None]]

    def __init__(self, multiplexer: Multiplexer, channel):
        multiplexer.remote_senders.append(self)
        self.multiplexer = multiplexer
        self.channel = channel
        self.destroy_callbacks = []

    def on_destroy(self, callback: Callable[[], None]):
        self.destroy_callbacks.append(callback)
    
    def destroy(self):
        for callback in self.destroy_callbacks:
            callback()
        self.multiplexer = None

    def send(self, message: Any):
        self.multiplexer.send(message, self.channel)
