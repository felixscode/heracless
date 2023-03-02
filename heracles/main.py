"""
heracles YAML TO PyObsject parser

"""
from typing import Callable, Dict
from pathlib import Path
from yaml import full_load
import os
from heracles.utils.exeptions import DirectoryError
from heracles.utils.cfg_tree import (
    Tree,
    tree_parser,
    tree_to_string_translator,
    tree_to_config_obj,
)


DEFAULT_DIR = Path(__file__).parent.resolve() / Path("./tests/test_config.yaml")
DEFAULT_DUMP_DIR = Path(__file__).parent.resolve() / Path("./tests/config/types.py")


def path_exists(path: Path):
    if not os.path.exists(path):
        raise DirectoryError(path)


def load_as_dict(cfg_dir: Path, yaml_load_func: Callable) -> dict:
    path_exists(cfg_dir)
    stream = open(cfg_dir, "r")
    return yaml_load_func(stream)


def dump_in_console(frozen, cfg_tree: Tree, *args, **kwargs) -> None:
    """
    console dumper: prints generated config object type into console
    """
    print(tree_to_string_translator(frozen, cfg_tree))


def dump_dummy(*args, **kwargs) -> None:
    """
    dummy dumper: can be used to bypass dumping
    """
    pass


def dump_in_file(frozen: bool, cfg_tree: Tree, dump_dir: Path) -> None:
    """
    file dumper: dumps config types into a file
    """
    path_exists(dump_dir)
    with open(dump_dir, "w") as dd:
        string = tree_to_string_translator(frozen, cfg_tree)
        dd.write(string)


def main(
    cfg_dir: Path,
    dump_dir: Path,
    dump_func: Callable,
    yaml_load_func: Callable,
    frozen: bool,
):
    cfg_dict = load_as_dict(cfg_dir, yaml_load_func)
    cfg_tree = tree_parser(cfg_dict)
    dump_func(
        frozen,
        cfg_tree,
        dump_dir,
    )
    return tree_to_config_obj(frozen, cfg_tree)


if __name__ == "__main__":
    cfg = main(DEFAULT_DIR, DEFAULT_DUMP_DIR, dump_in_file, full_load, True)
    print(cfg)
