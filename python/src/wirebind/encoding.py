from __future__ import annotations

from typing import TYPE_CHECKING

import cbor2

from .binds import Packable
from .binds.atom import Atom
from .message import Message
from .sender import Sender, RemoteSender

SENDER_TAG = 40987
SYNC_TAG = 40988

if TYPE_CHECKING:
    from .multiplex import Multiplexer


PACK_TYPES = {
    "atom": Atom,
}


class Encoder:
    def __init__(self, multiplexer: Multiplexer):
        self.multiplexer = multiplexer

    def default_encoder(self, encoder, v):
        if isinstance(v, Sender):
            channel = self.multiplexer.register_sender(v)
            encoder.encode(cbor2.CBORTag(SENDER_TAG, channel))
        elif isinstance(v, Packable):
            encoder.encode(cbor2.CBORTag(SYNC_TAG, v.pack()))
        else:
            raise TypeError(f"Unknown type: {type(v)}")

    def tag_hook(self, _decoder, tag, _shareable_index=False):
        if tag.tag == SENDER_TAG:
            return RemoteSender(self.multiplexer, tag.value)
        elif tag.tag == SYNC_TAG:
            packed = tag.value
            pack_type = packed["type"]
            if pack_type in PACK_TYPES:
                return PACK_TYPES[pack_type].from_packed(packed)
            else:
                raise TypeError(f"Unknown pack type: {pack_type}")
        else:
            raise TypeError(f"Unknown tag: {tag}")

    def encode(self, message: Message) -> bytes:
        return cbor2.dumps(message.to_dict(), default=self.default_encoder)

    def decode(self, data: bytes) -> Message:
        result = cbor2.loads(data, tag_hook=self.tag_hook)
        return Message.from_dict(result)
