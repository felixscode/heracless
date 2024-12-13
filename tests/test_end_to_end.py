"""
testing the app
"""

from dataclasses import asdict
from pathlib import Path

from yaml import full_load

from heracless.utils import as_dict, from_dict, mutate_config
from heracless.fight import fight as load_config, load_as_dict
from heracless.utils.cfg_tree import Tree, tree_parser
from tests.conftest import cfg_dict

TEST_DIR = Path(__file__).parent.resolve() / Path("./test_config.yaml")
TEST_DUMP_DIR = Path(__file__).parent.resolve() / Path("./config/types.py")

def test_cfg_tree_loading(cfg_dict):
    _cfg_dict = load_as_dict(TEST_DIR, full_load)
    assert type(tree_parser(cfg_dict)) == Tree
    assert _cfg_dict == cfg_dict

def test_full_0():
    cfg_path = TEST_DIR
    dump_dir = Path("./tests/config/types.py")
    config = load_config(cfg_dir=cfg_path, dump_dir=dump_dir, frozen=True)
    _dict = as_dict(config)
    _config = from_dict(_dict)
    config = mutate_config(config, "invoice", 0)
    assert config.invoice == 0
