# TYPEVARS and mixin classes

from typing import TypeVar, Type, Callable, Coroutine

H = TypeVar('H', bound='Hashable')  # Hashable object
_C = Callable[..., Coroutine]
T = TypeVar('T')

class Hashable:
    __slots__ = ()

    id: int

    def __eq__(self, O: Type[H]) -> bool:
        return self.id == O.id

    def __ne__(self, O: Type[H]) -> bool:
        return self.id != O.id

    def __hash__(self) -> int:
        return self.id >> 22
