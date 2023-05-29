from wirebind.sync_map import SyncMap, ID, MUTATION
from queue import Queue
from .util import never_called

def test_optimistic_apply():
    q = Queue()
    sm = SyncMap(q.put)

    sm['a'] = 1
    assert sm['a'] == 1
    assert q.get(False)[MUTATION] == {'a': [1]}

    sm['b'] = 2
    assert sm['b'] == 2
    assert q.get(False)[MUTATION] == {'b': [2]}


def test_server_mutation():
    sm = SyncMap(never_called)

    sm.apply({ID: "tmp", MUTATION: {'a': [1]}})
    assert sm['a'] == 1


def test_optimistic_precedence():
    """Optimistic local changes should take precedence over server changes."""
    q = Queue()
    sm = SyncMap(q.put)

    sm['a'] = 1
    assert sm['a'] == 1

    sm.apply({ID: "tmp", MUTATION: {'a': [2]}})
    assert sm['a'] == 1


def test_optimistic_reset_once_acked():
    """Optimistic local changes should stop taking precedence once the server
    acknowledges them."""
    q = Queue()
    sm = SyncMap(q.put)

    sm['a'] = 1
    assert sm['a'] == 1

    sm.apply({ID: "tmp", MUTATION: {'a': [2]}})
    assert sm['a'] == 1

    sm.apply(q.get(False))
    assert sm['a'] == 1

    sm.apply({ID: "tmp", MUTATION: {'a': [2]}})
    assert sm['a'] == 2


def test_explicit_optimistic_reset():
    sm = SyncMap(lambda _: None)

    sm['a'] = 1
    assert sm['a'] == 1

    sm.optimistic_reset()

    assert sm.get('a') is None


def test_optimistic_reset_with_newer_change():
    """If the local data structure has had two changes to the same key, the server
    acknowledging one should not override the other."""
    q = Queue()
    sm = SyncMap(q.put)

    sm['a'] = 1
    assert sm['a'] == 1
    sm['a'] = 2
    assert sm['a'] == 2

    sm.apply(q.get(False))
    assert sm['a'] == 2

    sm.apply(q.get(False))
    assert sm['a'] == 2


def test_optimistic_round_trip():
    """If a value changes from a to b to a, the first mutation to value a should not
    override the second mutation to value a.
    """
    q = Queue()
    sm = SyncMap(q.put)

    sm['a'] = 1
    assert sm['a'] == 1
    sm['a'] = 2
    assert sm['a'] == 2
    sm['a'] = 1
    assert sm['a'] == 1

    sm.apply(q.get(False))
    assert sm['a'] == 1
    sm.apply(q.get(False))
    assert sm['a'] == 1
    sm.apply(q.get(False))
    assert sm['a'] == 1


def test_del():
    """Deleting a key should remove it from the map."""
    q = Queue()
    sm = SyncMap(q.put)

    sm['a'] = 1
    assert sm['a'] == 1

    del sm['a']
    assert 'a' not in sm
    assert sm.get('a') is None


def test_store_none():
    """We can store a None value as distinct from being unset."""
    q = Queue()
    sm = SyncMap(q.put)

    assert 'a' not in sm
    sm['a'] = 1
    assert sm['a'] == 1
    assert 'a' in sm

    sm['a'] = None
    assert sm['a'] is None
    assert 'a' in sm

    sm.apply(q.get(False))

    assert sm['a'] is None
    assert 'a' in sm

    del sm['a']
    assert 'a' not in sm

    sm.apply(q.get(False))
    sm.apply(q.get(False))
    
    assert 'a' not in sm

    sm.optimistic_reset()
    assert 'a' not in sm
