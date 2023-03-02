"""
testing the app
"""
from heracles.decorator import heracles
from heracles.tests.load import filled_config, cfg_dict as correct_dict
from heracles.main import load_as_dict, DEFAULT_DIR
from yaml import full_load
from heracles.utils.cfg_tree import tree_parser, Tree
from heracles.tests.config.types import Config
import pytest
from dataclasses import asdict


@heracles()
def decorator_dummy(cfg):
    return cfg


def test_decorator(cfg_type):
    cfg = decorator_dummy()
    assert asdict(cfg) == asdict(cfg_type)


def test_cfg_tree_loading():
    cfg_dict = load_as_dict(DEFAULT_DIR, full_load)
    assert type(tree_parser(cfg_dict)) == Tree
    assert cfg_dict == correct_dict


@heracles()
def test_output_config_type(cfg):
    assert type(cfg).__name__ == "Config"
