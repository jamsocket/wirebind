from . import random_mutation_id, ID, MUTATION, Syncable

class SyncMap(Syncable):
    def __init__(self):
        super().__init__()
        self._map = {}

        # Map of key -> (mutation_id, (value,))
        self._optimistic = {}
    
    def __repr__(self) -> str:
        return repr(self._map)

    def __setitem__(self, key, value):
        id = self.emit({key: [value]})
        self._optimistic[key] = (id, (value,))

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __getitem__(self, key):
        if key in self._optimistic:
            if self._optimistic[key][1] is None:
                raise KeyError(key)
            return self._optimistic[key][1][0]
        return self._map[key]
    
    def __delitem__(self, key):
        id = self.emit({key: None})
        self._optimistic[key] = (id, None)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def optimistic_reset(self):
        self._optimistic = {}

    def apply(self, mutation):
        for key in mutation[MUTATION].keys():
            if key in self._optimistic:
                if self._optimistic[key][0] == mutation[ID]:
                    del self._optimistic[key]
        for k, v in mutation[MUTATION].items():
            if v is None:
                del self._map[k]
            else:
                self._map[k] = v[0]

    def __iter__(self):
        # iterate over both optimistic and non-optimistic keys, in order.
        for key in sorted(set(self._map.keys()) | set(self._optimistic.keys())):
            if key in self:
                yield key

    def __len__(self):
        return len(list(iter(self)))

    def items(self):
        for key in self:
            yield key, self[key]
