"""
heracless YAML TO PyObject parser

"""
import os
from pathlib import Path
from typing import Callable

from yaml import full_load

from heracless.utils.cfg_tree import (Tree, tree_parser, tree_to_config_obj,
                                      tree_to_string_translator)
from heracless.utils.utils import path_exists


DEFAULT_DIR = Path("./config/config.yaml")



def load_as_dict(cfg_dir: Path, yaml_load_func: Callable) -> dict:
    path_exists(cfg_dir)
    if os.stat(cfg_dir).st_size == 0:
        raise ValueError("Empty config file")
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


def dump_in_file(frozen: bool, cfg_tree: Tree, dump_dir: Path) -> None:
    """
    file dumper: dumps config types into a file
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
    dump_func: Callable,
    yaml_load_func: Callable,
    frozen: bool,
):
    cfg_dict = load_as_dict(cfg_dir, yaml_load_func)
    if cfg_dict is None:  # in case  dict is empty and config
        return None
    cfg_tree = tree_parser(cfg_dict)
    dump_func(
        frozen,
        cfg_tree,
        dump_dir,
    )
    config_obj =  tree_to_config_obj(frozen, cfg_tree)
    return config_obj

def fight(
    cfg_dir: Path,
    dump_dir: Path,
    frozen: bool):
    dump_func = dump_in_file
    yaml_load_func = full_load
    return _fight_hydra(cfg_dir, dump_dir, dump_func, yaml_load_func, frozen)



if __name__ == "__main__":
    cfg = fight(DEFAULT_DIR, Path("./tmp/test_file.py"), True)
    print(cfg)
