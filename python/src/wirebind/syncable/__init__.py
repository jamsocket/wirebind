import random

ID = "i"
MUTATION = "m"

def random_mutation_id():
    return random.randint(0, 2**64)
