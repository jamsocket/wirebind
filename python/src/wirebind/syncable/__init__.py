from abc import ABC, abstractmethod
import random

ID = "i"
MUTATION = "m"

def random_mutation_id():
    return random.randint(0, 2**64)


class Syncable(ABC):
    callback: any
    
    def __init__(self, callback):
        self.callback = callback

    @abstractmethod
    def optimistic_reset(self):
        pass

    @abstractmethod
    def apply(self, mutation: any):
        pass
