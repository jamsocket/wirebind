from . import random_mutation_id, ID, MUTATION, Syncable

class SyncValue(Syncable):
    def __init__(self, value):
        super().__init__()

        self._value = value
        # Optional[(mutation_id, (value,))]
        self._optimistic = None
    
    def __repr__(self) -> str:
        return f"SyncValue({self.get()})"

    def set(self, value):
        id = self.emit(value)
        self._optimistic = (id, (value,))
        
    def get(self):
        if self._optimistic is not None:
            return self._optimistic[1][0]
        return self._value

    def optimistic_reset(self):
        self._optimistic = None
    
    def apply(self, mutation):
        if self._optimistic is not None:
            if self._optimistic[0] == mutation[ID]:
                self._optimistic = None
        self._value = mutation[MUTATION]
