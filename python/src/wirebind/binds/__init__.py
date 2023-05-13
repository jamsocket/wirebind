import abc

class Packable(abc.ABC):
    @abc.abstractmethod
    def pack(self) -> dict:
        pass

    @abc.abstractstaticmethod
    def from_packed(packed: dict):
        pass

    @abc.abstractstaticmethod
    def pack_type() -> str:
        pass
