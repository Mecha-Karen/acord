from typing import TypeVar, Type

H = TypeVar('H', 'Hashable')
class Hashable:
    __slots__ = ()

    id: int

    def __eq__(self, O: Type[H]) -> bool:
        return self.id == O.id

    def __ne__(self, O: Type[H]) -> bool:
        return self.id != O.id

    def __hash__(self) -> int:
        return self.id >> 22
