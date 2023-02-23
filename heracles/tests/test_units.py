from heracles.decorator import heracles
from heracles.main import load_as_dict
from yaml import full_load
from heracles.main import DEFAULT_DIR, DEFAULT_DUMP_DIR, path_exists
from heracles.tests.load import filled_config, cfg_dict
from heracles.utils import exeptions, cfg_tree
import pytest


def test_dict_loading():
    assert load_as_dict(DEFAULT_DIR, full_load) == cfg_dict


def test_dir_error():
    with pytest.raises(Exception) as e_info:
        path_exists("some_test_path.test_path")


class CfgTree:
    def test_cfg_leaf_creation(cfg_leaf_int):
        cfg_leaf = cfg_tree.CfgLeaf.from_dict(cfg_leaf_int)
        assert cfg_leaf.name == "int_number"
        assert cfg_leaf.value == 4
        assert cfg_leaf.type == int

    def test_cfg_leaf_creation_unvalid(cfg_leaf_unvalid):
        pass
