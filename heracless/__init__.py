"""
This module provides the main entry points for the Heracless Client Tool.
"""

from heracless.decorator import heracless
from heracless.utils.helper import from_dict, mutate_config, as_dict
from heracless.main import DEFAULT_DIR, DEFAULT_DUMP_DIR
from heracless.main import main as _main
from heracless.main import dump_in_file as _default_dump_func
from yaml import full_load as _default_yaml_load
from heracless.cli_tool import run_cli as _run_cli
from pathlib import Path
from heracless.utils.c_types import Config


def load_config(
    cfg_path: Path = DEFAULT_DIR, dump_dir: Path = DEFAULT_DUMP_DIR, make_dir: bool = True, frozen: bool = True
) -> Config:
    """
    Load the configuration from the specified directory and return a Config object.

    Args:
        cfg_path (Path): The path to the configuration directory. Defaults to DEFAULT_DIR.
        dump_dir (Path): The path to the dump directory. Defaults to DEFAULT_DUMP_DIR.
        make_dir (bool): Whether to create the dump directory if it doesn't exist. Defaults to True.
        frozen (bool): Whether the configuration should be frozen. Defaults to True.

    Returns:
        Config: The loaded configuration.

    """
    return _main(
        cfg_dir=cfg_path,
        dump_dir=dump_dir,
        dump_func=_default_dump_func,
        yaml_load_func=_default_yaml_load,
        make_dir=make_dir,
        frozen=frozen,
    )


if __name__ == "__main__":
    _run_cli()
