"""
testing the app
"""

from dataclasses import asdict
from pathlib import Path

from yaml import full_load

from heracless.decorator import heracless
from heracless.main import load_as_dict
from heracless.tests.load import cfg_dict as correct_dict
from heracless.utils.cfg_tree import Tree, tree_parser

TEST_DIR = Path(__file__).parent.resolve() / Path("./test_config.yaml")
TEST_DUMP_DIR = Path(__file__).parent.resolve() / Path("./config/types.py")


@heracless(cfg_path=TEST_DIR, dump_dir=TEST_DUMP_DIR)
def decorator_dummy(cfg):
    return cfg


def test_decorator(cfg_type):
    cfg = decorator_dummy()
    assert asdict(cfg) == asdict(cfg_type)


def test_cfg_tree_loading():
    cfg_dict = load_as_dict(TEST_DIR, full_load, False)
    assert type(tree_parser(cfg_dict)) == Tree
    assert cfg_dict == correct_dict


@heracless(cfg_path=TEST_DIR, dump_dir=TEST_DUMP_DIR)
def test_output_config_type(cfg):
    assert type(cfg).__name__ == "Config"
