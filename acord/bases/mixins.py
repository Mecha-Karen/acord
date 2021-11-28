# TYPEVARS and mixin classes

from typing import TypeVar, Callable, Coroutine

H = TypeVar("H", bound="Hashable")  # Hashable object
_C = Callable[..., Coroutine]
T = TypeVar("T")


class Hashable:
    __slots__ = ()

    id: int

    def __eq__(self, O) -> bool:
        return self.id == getattr(O, "id", O)

    def __ne__(self, O) -> bool:
        return self.id != getattr(O, "id", O)

    def __hash__(self) -> int:
        return self.id >> 22
