from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .sender import AbstractSender


class BroadcastList:
    map: Dict[int, Any]
    next_id = 0

    def __init__(self):
        self.map = dict()

    def __iter__(self):
        return iter(self.map.values())
    
    def send(self, message: Any):
        for item in self:
            item.send(message)

    def add(self, item: AbstractSender):
        handle = self.next_id
        self.next_id += 1
        self.map[handle] = item
        item.on_destroy(lambda: self.remove(handle))

    def remove(self, handle: int):
        if handle in self.map:
            del self.map[handle]
        else:
            print("Handle already removed.")
