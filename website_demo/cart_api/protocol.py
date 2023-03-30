from typing_extensions import Protocol

class Merchandise(Protocol):
    pk: int
    name: str
    price: int
    status: str
    inventory: int
    sale_price: int = None

    def __str__(self) -> str:
        return self.name