from heracles.decorator import heracles
from heracles.main import load_as_dict
from yaml import full_load
from heracles.main import DEFAULT_DIR, DEFAULT_DUMP_DIR, path_exists
from heracles.tests.load import filled_config, cfg_dict
from heracles.utils import exeptions
import pytest


def test_dict_loading():
    assert load_as_dict(DEFAULT_DIR, full_load) == cfg_dict


def test_dir_error():
    with pytest.raises(Exception) as e_info:
        path_exists("some_test_path.test_path")
