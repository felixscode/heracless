from dataclasses import dataclass
from datetime import datetime
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Config:
    invoice: int
    date: date
    bill_to: "BillTo"
    ship_to: "ShipTo"
    product: tuple["ProductItem"]
    tax: float
    total: float
    comments: str


@dataclass(frozen=True)
class BillTo:
    given: str
    family: str
    address: "Address"


@dataclass(frozen=True)
class Address:
    lines: str
    city: str
    state: str
    postal: int


@dataclass(frozen=True)
class ProductItem:
    sku: str
    quantity: int
    description: str
    price: float


@dataclass(frozen=True)
class ShipTo:
    given: str
    family: str
    address: "Address"


def load_config(config_path: str) -> Config: ...
