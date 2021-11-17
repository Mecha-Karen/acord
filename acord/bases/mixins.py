class Hashable:
    __slots__ = ()

    id: int

    def __eq__(self, O) -> bool:
        return self.id == O.id

    def __ne__(self, O) -> bool:
        return self.id != O.id

    def __hash__(self) -> int:
        return self.id >> 22
