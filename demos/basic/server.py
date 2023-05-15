import asyncio
from typing import Optional

from wirebind.rpc import expose
from wirebind.binds.atom import Atom
from wirebind.sender import Sender


class Slider:
    value = Atom(50)


class Timer:
    value = Atom(0)
    task: Optional[asyncio.Task]

    def __init__(self):
        self.task = None

    @expose("start")
    def start(self):
        if self.task is not None:
            return
        self.task = asyncio.create_task(self.incr())

    @expose("stop")
    def stop(self):
        self.task.cancel()
        self.task = None

    @expose("reset")
    def reset(self):
        self.value.set(0)

    async def incr(self):
        while True:
            await asyncio.sleep(0.1)
            self.value.set(self.value.get() + 1)


class Counter:
    def __init__(self):
        self.count = Atom(0)

    @expose("inc")
    def inc(self):
        self.count.set(self.count.get() + 1)

    @expose("dec")
    def dec(self):
        self.count.set(self.count.get() - 1)


class Calc:
    hidden_register = None
    operation = None
    next_action_clears = False
    display = Atom(0)

    def op(self):
        if self.hidden_register is None:
            raise Exception("No hidden register")
        elif self.operation is None:
            raise Exception("No operation")
        elif self.operation == "+":
            self.display.set(self.hidden_register + self.display.get())
        elif self.operation == "-":
            self.display.set(self.hidden_register - self.display.get())
        elif self.operation == "*":
            self.display.set(self.hidden_register * self.display.get())
        elif self.operation == "/":
            self.display.set(self.hidden_register / self.display.get())
        else:
            raise Exception("Unknown operation")
        self.hidden_register = None
        self.operation = None

    @expose("clear")
    def press_clear(self):
        self.display.set(0)
        self.hidden_register = None
        self.operation = None

    @expose("digit")
    def press_digit(self, digit: int):
        if self.next_action_clears:
            self.display.set(0)
            self.next_action_clears = False
        if self.display.get() == 0:
            self.display.set(digit)
        else:
            self.display.set(self.display.get() * 10 + digit)

    @expose("op")
    def press_operation(self, op: str):
        if op not in ["+", "-", "*", "/"]:
            raise Exception(f"Unknown operation {op}")
        self.hidden_register = self.display.get()
        self.operation = op
        self.next_action_clears = True

    @expose("eq")
    def press_eq(self):
        self.op()
        self.hidden_register = None
        self.operation = None
        self.next_action_clears = True


GLOBAL_STATE = {
    "slider": Slider(),
    "timer": Timer(),
    "counter": Counter(),
    "calc": Calc(),
}


def root(message: any):
    typ = message["typ"]
    reply = message["reply"]

    if typ in GLOBAL_STATE:
        obj = GLOBAL_STATE[typ]
        # Iterate over the fields in obj, and send the ones that implement
        # Packable to the client.
        result = {}

        for field_name in dir(obj):
            field = getattr(obj, field_name)
            if isinstance(field, Atom):
                result[field_name] = field

            # If the field is a method check if it is exposed and if so
            # add it to the result.
            if hasattr(field, "_exposed_as"):
                result[field._exposed_as] = Sender(
                    lambda args, field=field: field(**(args or {}))
                )

        reply.send(result)
