from dataclasses import dataclass
from datetime import datetime
from datetime import date
from pathlib import Path
import pytest


# @dataclass(frozen=True)
# class Address:
#     lines: str
#     city: str
#     state: str
#     postal: str


# @dataclass(frozen=True)
# class ProductItem:
#     sku: str
#     quantity: int
#     description: str
#     price: float


# @dataclass(frozen=True)
# class Config:
#     invoice: int
#     date: date
#     bill_to: "BillTo"
#     ship_to: "ShipTo"
#     product: tuple["ProductItem"]
#     tax: float
#     total: float
#     comments: str


# @dataclass(frozen=True)
# class ShipTo:
#     given: str
#     family: str
#     address: "Address"


# @dataclass(frozen=True)
# class BillTo:
#     given: str
#     family: str
#     address: "Address"


@pytest.fixture
def cfg_dict():
    return {
        "invoice": 34843,
        "date": date(2001, 1, 23),
        "bill-to": {
            "given": "Chris",
            "family": "Dumars",
            "address": {
                "lines": "458 Walkman Dr.\nSuite #292\n",
                "city": "Royal Oak",
                "state": "MI",
                "postal": 48046,
            },
        },
        "ship-to": {
            "given": "Chris",
            "family": "Dumars",
            "address": {
                "lines": "458 Walkman Dr.\nSuite #292\n",
                "city": "Royal Oak",
                "state": "MI",
                "postal": 48046,
            },
        },
        "product": [
            {"sku": "BL394D", "quantity": 4, "description": "Basketball", "price": 450.0},
            {"sku": "BL4438H", "quantity": 1, "description": "Super Hoop", "price": 2392.0},
        ],
        "tax": 251.42,
        "total": 4443.52,
        "comments": "Late afternoon is best. Backup contact is Nancy Billsmer @ 338-4338.",
    }
