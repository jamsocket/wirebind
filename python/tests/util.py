import json
from wirebind.multiplex import Multiplexer
from queue import Queue


class WrappedQueue:
    def __init__(self):
        self.q = Queue()

    def put(self, v):
        self.q.put(json.dumps(v))

    def get(self):
        return json.loads(self.q.get(False))


def never_called(_):
    assert False, "This function should never be called."


def multiplexer_pair():
    server = Multiplexer(never_called)
    client = Multiplexer(server.receive)
    server.send_function = client.receive

    return server, client
