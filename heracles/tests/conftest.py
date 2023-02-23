import pytest


@pytest.fixture(scope="module")
def cfg_leaf_int():
    return {"int_number": int(4)}


@pytest.fixture(scope="module")
def cfg_leaf_unvalid():
    return {"int_number": int(3), "float_number": float(4)} @ pytest.fixture(
        scope="module"
    )
