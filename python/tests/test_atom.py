from queue import Queue
from .util import multiplexer_pair
from wirebind.binds.atom import Atom, AtomReplica


def test_atom_becomes_replica():
    atom = Atom(4)
    server, client = multiplexer_pair()

    q = Queue()
    server.set_root(q.put)

    client.send_root(atom)

    replica = q.get(False)
    assert isinstance(replica, AtomReplica)
    assert replica.value == 4


def test_atom_replica_updates():
    atom = Atom(4)
    server, client = multiplexer_pair()

    q = Queue()
    server.set_root(q.put)

    client.send_root(atom)

    replica = q.get(False)
    replica.set(5)

    assert atom.value == 5


def test_atom_updates():
    atom = Atom(4)
    server, client = multiplexer_pair()

    q = Queue()
    server.set_root(q.put)

    client.send_root(atom)

    replica = q.get(False)
    atom.set(5)
    print(atom.value, atom.listeners)

    assert replica.value == 5
