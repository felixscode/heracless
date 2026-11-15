from datetime import date
from pathlib import Path
from typing import Any

import pytest

TEST_CONFIG = Path(__file__).parent / "test_config.yaml"


@pytest.fixture
def config_path() -> Path:
    """The invoice example from the YAML spec (uses anchors, dates, block scalars)."""
    return TEST_CONFIG


@pytest.fixture
def cfg_dict() -> dict[str, Any]:
    """What `config_path` parses to."""
    address = {
        "lines": "458 Walkman Dr.\nSuite #292\n",
        "city": "Royal Oak",
        "state": "MI",
        "postal": 48046,
    }
    return {
        "invoice": 34843,
        "date": date(2001, 1, 23),
        "bill-to": {"given": "Chris", "family": "Dumars", "address": address},
        "ship-to": {"given": "Chris", "family": "Dumars", "address": address},
        "product": [
            {"sku": "BL394D", "quantity": 4, "description": "Basketball", "price": 450.0},
            {"sku": "BL4438H", "quantity": 1, "description": "Super Hoop", "price": 2392.0},
        ],
        "tax": 251.42,
        "total": 4443.52,
        "comments": "Late afternoon is best. Backup contact is Nancy Billsmer @ 338-4338.",
    }
