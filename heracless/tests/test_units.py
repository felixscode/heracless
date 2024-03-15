from pathlib import Path

import pytest
from yaml import full_load

from heracless.main import load_as_dict, path_exists
from heracless.tests.load import cfg_dict
from heracless.utils import cfg_tree
from heracless import as_dict, from_dict, mutate_config, load_config

TEST_DIR = Path(__file__).parent.resolve() / Path("./test_config.yaml")
DUMP_DIR = Path(__file__).parent.resolve() / Path("./conftest.py")


def test_dict_loading():
    assert load_as_dict(TEST_DIR, full_load, False) == cfg_dict


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
    config = load_config(cfg_path=TEST_DIR, dump_dir=DUMP_DIR)
    assert config.invoice == 34843


def test_dict_helpers():
    config = load_config(cfg_path=TEST_DIR, dump_dir=DUMP_DIR)
    _dict = as_dict(config)
    _config = from_dict(_dict)
    assert config.invoice == _config.invoice


def test_mutatate():
    config = load_config(cfg_path=TEST_DIR, dump_dir=DUMP_DIR)
    config = mutate_config(config, "invoice", 0)
    assert config.invoice == 0
