from . import Syncable, MUTATION, ID

APPLY = "apply"
KIND = "k"
VALUE = "v"


class SyncMap(Syncable):
    def __init__(self, value=None):
        super().__init__()
        self._map = value or dict()

        # Map of key -> (mutation_id, (value,))
        self._optimistic = {}

    def __repr__(self) -> str:
        return repr(self._map)

    def repr_json(self):
        return dict(self.items())

    def __setitem__(self, key, value):
        repr_value = {VALUE: value}
        if isinstance(value, Syncable):
            repr_value = {KIND: value.__class__.__name__, VALUE: value.repr_json()}
            value.set_parent(lambda mutation: self.nest_emit(mutation, key))
        id = self.emit({key: repr_value})
        self._optimistic[key] = (id, (value,))

    def nest_emit(self, mutation, key):
        if self.callback is not None:
            self.callback(
                {ID: mutation[ID], MUTATION: {key: {"apply": mutation[MUTATION]}}}
            )

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

    def apply_mut(self, mutation, id):
        for key in mutation.keys():
            if key in self._optimistic:
                if self._optimistic[key][0] == id:
                    del self._optimistic[key]
        for k, v in mutation.items():
            print("k", k, "v", v)
            if v is None:
                del self._map[k]
            elif KIND in v:
                ob = globals()[v[KIND]](v[VALUE])
                self._map[k] = ob
                # ob.set_parent(lambda v: v.nest_emit(mutation, k))
            elif VALUE in v:
                self._map[k] = v[VALUE]
            elif APPLY in v:
                print("h1")
                self._map[k].apply_mut(v[APPLY], id)
                print("h2")
            else:
                raise ValueError("Invalid mutation value: {}".format(v))

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
