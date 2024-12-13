"""
heracless YAML TO PyObject parser

"""

import os
from pathlib import Path
from typing import Callable, Optional, Any

from yaml import full_load

from heracless.utils.cfg_tree import (Tree, tree_parser, tree_to_config_obj,
                                      tree_to_string_translator)
from heracless.utils.utils import path_exists
from heracless.utils.exceptions import YamlSyntaxError

DEFAULT_DIR = Path("./config/config.yaml")


def load_as_dict(cfg_dir: Path, yaml_load_func: Callable[[Any], dict]) -> dict:
    """
    Load a YAML configuration file and return it as a dictionary.

    :param cfg_dir: Path to the YAML configuration file.
    :param yaml_load_func: Function to load YAML content.
    :return: Dictionary representation of the YAML content.
    :raises ValueError: If the config file is empty.
    :raises FileNotFoundError: If the config file does not exist.
    :raises OSError: If there is an issue reading the file.
    """
    path_exists(cfg_dir)
    if os.stat(cfg_dir).st_size == 0:
        raise ValueError("Empty config file")
    stream = open(cfg_dir, "r")
    try:
        return yaml_load_func(stream)
    except Exception as e:
        raise YamlSyntaxError(str(e))


def dump_in_console(frozen: bool, _: Any, cfg_tree: Tree, *args: Any, **kwargs: Any) -> None:
    """
    Console dumper: prints generated config object type into console.

    :param frozen: Whether the config object is frozen.
    :param _: Unused parameter.
    :param cfg_tree: Configuration tree.
    :param args: Additional arguments.
    :param kwargs: Additional keyword arguments.
    """
    print(tree_to_string_translator(frozen, cfg_tree))


def dump_dummy(*args: Any, **kwargs: Any) -> None:
    """
    Dummy dumper: can be used to bypass dumping.

    :param args: Additional arguments.
    :param kwargs: Additional keyword arguments.
    """


def dump_in_file(frozen: bool, cfg_tree: Tree, dump_dir: Path) -> None:
    """
    File dumper: dumps config types into a file.

    :param frozen: Whether the config object is frozen.
    :param cfg_tree: Configuration tree.
    :param dump_dir: Directory to dump the config file.
    :raises FileNotFoundError: If the dump directory does not exist.
    :raises OSError: If there is an issue writing to the file.
    """
    if not dump_dir.suffix == ".pyi":
        dump_dir = dump_dir.with_suffix(".pyi")
    path_exists(dump_dir)
    with open(dump_dir, "w") as dd:
        string = tree_to_string_translator(frozen, cfg_tree)
        dd.write(string)


def _fight_hydra(
    cfg_dir: Path,
    dump_dir: Path,
    dump_func: Callable[[bool, Tree, Path], None],
    yaml_load_func: Callable[[Any], dict],
    frozen: bool,
) -> Optional[Any]:
    """
    Internal function to parse YAML config and dump it using the specified function.

    :param cfg_dir: Path to the YAML configuration file.
    :param dump_dir: Directory to dump the config file.
    :param dump_func: Function to dump the config.
    :param yaml_load_func: Function to load YAML content.
    :param frozen: Whether the config object is frozen.
    :return: Configuration object or None if the config is empty.
    :raises ValueError: If the config file is empty.
    :raises FileNotFoundError: If the config file does not exist.
    :raises OSError: If there is an issue reading the file.
    """
    cfg_dict = load_as_dict(cfg_dir, yaml_load_func)
    if cfg_dict is None:  # in case dict is empty and config
        return None
    cfg_tree = tree_parser(cfg_dict)
    dump_func(
        frozen,
        cfg_tree,
        dump_dir,
    )
    config_obj = tree_to_config_obj(frozen, cfg_tree)
    return config_obj


def fight(cfg_dir: Path, dump_dir: Path, frozen: bool) -> Optional[Any]:
    """
    Parse YAML config and dump it into a file.

    :param cfg_dir: Path to the YAML configuration file.
    :param dump_dir: Directory to dump the config file.
    :param frozen: Whether the config object is frozen.
    :return: Configuration object or None if the config is empty.
    :raises ValueError: If the config file is empty.
    :raises FileNotFoundError: If the config file does not exist.
    :raises OSError: If there is an issue reading the file.
    """
    dump_func = dump_in_file
    yaml_load_func = full_load
    return _fight_hydra(cfg_dir, dump_dir, dump_func, yaml_load_func, frozen)


if __name__ == "__main__":
    cfg = fight(DEFAULT_DIR, Path("./tmp/test_file.py"), True)
    print(cfg)
