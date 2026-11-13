from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Product:
    hash_: str
    slug: str

    def __hash__(self):
        return hash(self.hash_)


@dataclass(eq=True, frozen=True)
class Storage(Product):
    description: str
    series: str
    format_: str | None
    type_: str
    capacity_gb: int
    read: int | None
    write: int | None
    price_cents: int
    price_slip_cents: int
    sponsored: bool
