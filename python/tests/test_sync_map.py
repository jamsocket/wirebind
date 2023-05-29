from wirebind.syncable import ID, MUTATION
from wirebind.syncable.sync_map import SyncMap

from .util import never_called, WrappedQueue


def test_optimistic_apply():
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    sm['a'] = 1
    assert sm['a'] == 1
    assert q.get()[MUTATION] == {'a': [1]}

    sm['b'] = 2
    assert sm['b'] == 2
    assert q.get()[MUTATION] == {'b': [2]}


def test_server_mutation():
    sm = SyncMap()
    sm.set_parent(never_called)

    sm.apply({ID: "tmp", MUTATION: {'a': [1]}})
    assert sm['a'] == 1


def test_optimistic_precedence():
    """Optimistic local changes should take precedence over server changes."""
    sm = SyncMap()

    sm['a'] = 1
    assert sm['a'] == 1

    sm.apply({ID: "tmp", MUTATION: {'a': [2]}})
    assert sm['a'] == 1


def test_optimistic_reset_once_acked():
    """Optimistic local changes should stop taking precedence once the server
    acknowledges them."""
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    sm['a'] = 1
    assert sm['a'] == 1

    sm.apply({ID: "tmp", MUTATION: {'a': [2]}})
    assert sm['a'] == 1

    sm.apply(q.get())
    assert sm['a'] == 1

    sm.apply({ID: "tmp", MUTATION: {'a': [2]}})
    assert sm['a'] == 2


def test_explicit_optimistic_reset():
    sm = SyncMap()

    sm['a'] = 1
    assert sm['a'] == 1

    sm.optimistic_reset()

    assert sm.get('a') is None


def test_optimistic_reset_with_newer_change():
    """If the local data structure has had two changes to the same key, the server
    acknowledging one should not override the other."""
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    sm['a'] = 1
    assert sm['a'] == 1
    sm['a'] = 2
    assert sm['a'] == 2

    sm.apply(q.get())
    assert sm['a'] == 2

    sm.apply(q.get())
    assert sm['a'] == 2


def test_optimistic_round_trip():
    """If a value changes from a to b to a, the first mutation to value a should not
    override the second mutation to value a.
    """
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    sm['a'] = 1
    assert sm['a'] == 1
    sm['a'] = 2
    assert sm['a'] == 2
    sm['a'] = 1
    assert sm['a'] == 1

    sm.apply(q.get())
    assert sm['a'] == 1
    sm.apply(q.get())
    assert sm['a'] == 1
    sm.apply(q.get())
    assert sm['a'] == 1


def test_del():
    """Deleting a key should remove it from the map."""
    sm = SyncMap()

    sm['a'] = 1
    assert sm['a'] == 1

    del sm['a']
    assert 'a' not in sm
    assert sm.get('a') is None


def test_store_none():
    """We can store a None value as distinct from being unset."""
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    assert 'a' not in sm
    sm['a'] = 1
    assert sm['a'] == 1
    assert 'a' in sm

    sm['a'] = None
    assert sm['a'] is None
    assert 'a' in sm

    sm.apply(q.get())

    assert sm['a'] is None
    assert 'a' in sm

    del sm['a']
    assert 'a' not in sm

    sm.apply(q.get())
    sm.apply(q.get())
    
    assert 'a' not in sm

    sm.optimistic_reset()
    assert 'a' not in sm


def test_iter_order():
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    sm['d'] = 4
    sm['b'] = 2
    sm['e'] = 5
    sm['a'] = 1
    sm['c'] = 3
    sm['f'] = 6

    for _ in range(6):
        keys = list(sm)
        assert keys == ['a', 'b', 'c', 'd', 'e', 'f']

        sm.apply(q.get())


def test_nest_map():
    q = WrappedQueue()
    sm = SyncMap()
    sm.set_parent(q.put)

    # sm['a'] = SyncMap()
    # sm['a']['b'] = 1

    # assert sm['a']['b'] == 1

    # sm.optimistic_reset()

    # mut = q.get()
    # print("mut", mut)
    # sm.apply(mut)
    # assert sm['a']['b'] == 1
    # assert False
