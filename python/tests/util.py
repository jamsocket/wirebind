from wirebind.multiplex import Multiplexer

def never_called(_):
    assert False, "This function should never be called."


def multiplexer_pair():
    server = Multiplexer(never_called)
    client = Multiplexer(server.receive)
    server.send_function = client.receive

    return server, client
