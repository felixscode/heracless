from datetime import datetime
from pathlib import Path

import pytest
from yaml import full_load

from heracless.utils import as_dict, from_dict, mutate_config
from heracless.fight import load_as_dict, path_exists,fight as load_config
from heracless.utils import cfg_tree
from tests.config.types import Config

TEST_DIR = Path(__file__).parent.resolve() / Path("./test_config.yaml")
DUMP_DIR = Path(__file__).parent.resolve() / Path("./conftest.py")


def test_dict_loading(cfg_dict):
    assert load_as_dict(TEST_DIR, full_load) == cfg_dict


def test_dir_error():
    with pytest.raises(Exception) as e_info:
        path_exists("some_test_path.test_path")


class TestTree:
    def test_iterable_generator(self):
        value, name = [2, 1], "a"
        out = tuple(cfg_tree.iterable_generator(value, name))
        assert out == (("a_item", 2), ("a_item", 1))
        value, name = {"a": 2}, "some_dict"
        out = tuple(cfg_tree.iterable_generator(value, name))
        assert out == (("a", 2),)


def test_load_config():
    config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
    assert config.invoice == 34843


def test_dict_helpers():
    config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
    _dict = as_dict(config)
    _config = from_dict(_dict)
    assert config.invoice == _config.invoice


def test_mutate():
    config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
    config = mutate_config(config, "invoice", 0)
    assert config.invoice == 0


# def test_config_type():
#     config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
#     assert isinstance(config, Config)


def test_config_values():
    config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
    assert config.invoice == 34843
    assert config.date == datetime.strptime("2001-01-23", "%Y-%m-%d").date()
    assert config.bill_to.given == "Chris"
    assert config.bill_to.family == "Dumars"
    assert config.bill_to.address.city == "Royal Oak"
    assert config.product[0].sku == "BL394D"
    assert config.product[0].quantity == 4
    assert config.product[0].description == "Basketball"
    assert config.product[0].price == 450.0
    assert config.tax == 251.42
    assert config.total == 4443.52
    assert config.comments == "Late afternoon is best. Backup contact is Nancy Billsmer @ 338-4338."


def test_mutate_nested():
    config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
    config = mutate_config(config, "bill_to.address.city", "New City")
    assert config.bill_to.address.city == "New City"


def test_as_dict():
    config = load_config(cfg_dir=TEST_DIR, dump_dir=DUMP_DIR, frozen=True)
    config_dict = as_dict(config)
    assert config_dict["invoice"] == 34843
    assert config_dict["bill_to"]["given"] == "Chris"
    assert config_dict["product"][0]["sku"] == "BL394D"
