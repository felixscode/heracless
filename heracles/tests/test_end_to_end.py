"""
testing the app
"""
from heracles.decorator import heracles
from heracles.tests.load import filled_config, cfg_dict as correct_dict
from heracles.main import load_as_dict, DEFAULT_DIR
from yaml import full_load
from heracles.utils.cfg_tree import dict_to_cfg_tree, CfgStruct
from heracles.tests.config.types import Config


@heracles()
def test_decorator(cfg):
    assert cfg == filled_config()


def test_cfg_tree_loading():
    cfg_dict = load_as_dict(DEFAULT_DIR, full_load)
    assert type(dict_to_cfg_tree(cfg_dict)) == CfgStruct
    assert cfg_dict == correct_dict


@heracles()
def test_output_config_type(cfg):
    assert type(cfg) == type


if __name__ == "__main__":
    test_cfg_tree_loading()
