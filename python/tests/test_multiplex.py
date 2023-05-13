from wirebind.sender import Sender
from wirebind.multiplex import Multiplexer
from queue import Queue


def never_called(_):
    assert False, "This function should never be called."


def multiplexer_pair():
    server = Multiplexer(never_called)
    client = Multiplexer(server.receive)
    server.send_function = client.receive

    return server, client


def test_multiplexer_local():
    q = Queue()
    sender = Sender(q.put)

    sender.send("Hello, world!")
    assert q.get(False) == "Hello, world!"


def test_simple_server():
    server, client = multiplexer_pair()

    q = Queue()
    server.set_root(q.put)

    client.send_root("Hello, world!")

    assert q.get(False) == "Hello, world!"


def test_simple_rpc():
    server, client = multiplexer_pair()

    def rpc(message):
        reply: Sender = message["reply"]
        reply.send("Hello, world!")

    server.set_root(rpc)

    q = Queue()
    ch = Sender(q.put)
    client.send_root({"reply": ch})

    assert q.get(False) == "Hello, world!"
