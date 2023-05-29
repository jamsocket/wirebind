from abc import ABC, abstractmethod
import random

ID = "i"
MUTATION = "m"

def random_mutation_id():
    return random.randint(0, 2**64)


class Syncable(ABC):
    callback: any = None
    
    def __init__(self):
        pass

    def emit(self, mutation):
        id = random_mutation_id()
        if self.callback is not None:
            self.callback({ID: id, MUTATION: mutation})
        return id
    
    def set_parent(self, parent):
        self.callback = parent

    @abstractmethod
    def optimistic_reset(self):
        pass

    def apply(self, mutation: any):
        self.apply_mut(mutation[MUTATION], mutation[ID])

    @abstractmethod
    def apply_mut(self, mutation: any, id: int):
        pass
