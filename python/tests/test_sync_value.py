from queue import Queue

from wirebind.syncable import MUTATION
from wirebind.syncable.sync_value import SyncValue


def test_optimistic_apply():
    q = Queue()
    sm = SyncValue(7, q.put)
    assert sm.get() == 7

    sm.set(1)
    assert sm.get() == 1
    assert q.get(False)[MUTATION] == 1


def test_optimistic_reset():
    q = Queue()
    sm = SyncValue(7, q.put)

    sm.set(1)
    assert sm.get() == 1

    sm.optimistic_reset()
    assert sm.get() == 7

    sm.apply(q.get(False))
    assert sm.get() == 1


