from __future__ import annotations

from typing import Callable, Dict, Any, List

from .message import Message
from .encoding import Encoder
from .sender import Sender, RemoteSender

# Well-known channels
ROOT = 0


class Multiplexer:
    registry: Dict[int, Callable[[Message]]]
    send_function: Callable[[bytes], None]
    next_channel: int = 1
    encoder: Encoder
    remote_senders: List[RemoteSender]

    def __init__(self, send_function: Callable[[bytes], None]):
        self.registry = dict()
        self.encoder = Encoder(self)
        self.send_function = send_function
        self.remote_senders = []

    def set_root(self, root: Callable[[Message], None]):
        """Set the root callback for this Multiplexer."""
        if self.registry.get(0) is not None:
            raise ValueError("Root callback already set")
        self.registry[0] = root

    def send_root(self, message: Any):
        """Send a message to the remote root callback."""
        self.send(message, ROOT)

    def send(self, message: Any, channel: int):        
        message = Message(message, channel)
        message_enc = self.encoder.encode(message)
        self.send_function(message_enc)

    def register_sender(self, sender: Sender) -> int:
        """Register a Sender and return its Address."""
        channel = self.next_channel
        self.next_channel += 1
        self.registry[channel] = sender.send
        return channel

    def receive(self, message_bytes: bytes):
        """Receive an inbound message and route it to the appropriate callback."""
        message = self.encoder.decode(message_bytes)
        self.registry[message.channel](message.message)

    def cleanup(self):
        for remote_sender in self.remote_senders:
            remote_sender.destroy()
        # We need to clean up some fields manually because they may contain
        # circular references. If we don't do this, the Multiplexer may never
        # be garbage collected.
        self.remote_senders = None
        self.encoder = None
        self.registry = None
