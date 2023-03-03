"""
heracless YAML TO PyObject parser

"""
import os
from pathlib import Path
from typing import Callable

from yaml import full_load

from heracless.utils.cfg_tree import (Tree, tree_parser, tree_to_config_obj,
                                      tree_to_string_translator)
from heracless.utils.exceptions import DirectoryError

DEFAULT_DIR = Path("./config/config.yaml")
DEFAULT_DUMP_DIR = Path("./config/types.py")


def path_exists(path: Path, create_path: bool):
    if not os.path.exists(path):
        if not create_path:
            raise DirectoryError(path)
        else:
            if not os.path.exists(path.parent):
                os.makedirs(path.parent)
            os.mknod(path)


def load_as_dict(cfg_dir: Path, yaml_load_func: Callable, make_dir: bool) -> dict:
    path_exists(cfg_dir, make_dir)
    stream = open(cfg_dir, "r")
    return yaml_load_func(stream)


def dump_in_console(frozen: bool, _, cfg_tree: Tree, *args, **kwargs) -> None:
    """
    console dumper: prints generated config object type into console
    """
    print(tree_to_string_translator(frozen, cfg_tree))


def dump_dummy(*args, **kwargs) -> None:
    """
    dummy dumper: can be used to bypass dumping
    """


def dump_in_file(frozen: bool, create_dir: bool, cfg_tree: Tree, dump_dir: Path) -> None:
    """
    file dumper: dumps config types into a file
    """
    path_exists(dump_dir, create_dir)
    with open(dump_dir, "w") as dd:
        string = tree_to_string_translator(frozen, cfg_tree)
        dd.write(string)


def main(
    cfg_dir: Path,
    dump_dir: Path,
    dump_func: Callable,
    yaml_load_func: Callable,
    make_dir: bool,
    frozen: bool,
):
    cfg_dict = load_as_dict(cfg_dir, yaml_load_func, make_dir)
    if cfg_dict is None:  # in case  dict is empty and config
        return None
    cfg_tree = tree_parser(cfg_dict)
    dump_func(
        frozen,
        make_dir,
        cfg_tree,
        dump_dir,
    )
    return tree_to_config_obj(frozen, cfg_tree)


if __name__ == "__main__":
    cfg = main(DEFAULT_DIR, DEFAULT_DUMP_DIR, dump_in_file, full_load, True, True)
    print(cfg)
