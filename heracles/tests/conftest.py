import datetime
from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class Address:
    lines: str
    city: str
    state: str
    postal: int


@dataclass(frozen=True)
class BillTo:
    given: str
    family: str
    address: Address


@dataclass(frozen=True)
class Address:
    lines: str
    city: str
    state: str
    postal: int


@dataclass(frozen=True)
class ShipTo:
    given: str
    family: str
    address: Address


@dataclass(frozen=True)
class ProductItem:
    sku: str
    quantity: int
    description: str
    price: float


@dataclass(frozen=True)
class Config:
    invoice: int
    date: datetime.date
    bill_to: BillTo
    ship_to: ShipTo
    product: list
    tax: float
    total: float
    comments: str


@pytest.fixture(scope="module")
def cfg_leaf_int():
    return {"int_number": int(4)}


@pytest.fixture(scope="module")
def cfg_leaf_invalid():
    return {"int_number": int(3), "float_number": float(4)} @ pytest.fixture(scope="module")


@pytest.fixture(scope="module")
def cfg_type() -> Config:
    return Config(
        invoice=34843,
        date=datetime.date(2001, 1, 23),
        bill_to=BillTo(
            given="Chris",
            family="Dumars",
            address=Address(
                lines="458 Walkman Dr.\nSuite #292\n",
                city="Royal Oak",
                state="MI",
                postal=48046,
            ),
        ),
        ship_to=ShipTo(
            given="Chris",
            family="Dumars",
            address=Address(
                lines="458 Walkman Dr.\nSuite #292\n",
                city="Royal Oak",
                state="MI",
                postal=48046,
            ),
        ),
        product=(
            ProductItem(sku="BL394D", quantity=4, description="Basketball", price=450.0),
            ProductItem(sku="BL4438H", quantity=1, description="Super Hoop", price=2392.0),
        ),
        tax=251.42,
        total=4443.52,
        comments="Late afternoon is best. Backup contact is Nancy Billsmer @ 338-4338.",
    )
