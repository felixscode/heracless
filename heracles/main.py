"""
heracles YAML TO PyObsject parser

"""
from typing import Callable, Dict
from pathlib import Path
from yaml import full_load
import os
from heracles.utils.exeptions import DirectoryError
from heracles.utils.expr_tree import CfgTree
from heracles.utils.expr_tree import dict_to_expr_tree


DEFAULT_DIR = Path(__file__).parent.resolve() / Path("./tests/test_config.yaml")
DEFAULT_DUMP_DIR = Path(__file__).parent.resolve() / Path("./tests/config/types.py")


def path_exists(path: Path):
    if not os.path.exists(path):
        raise DirectoryError(path)


def load_as_dict(cfg_dir: Path, yaml_load_func: Callable) -> dict:
    path_exists(cfg_dir)
    stream = open(cfg_dir, "r")
    return yaml_load_func(stream)


def dump_in_console(expr_tree: CfgTree, *args, **kwargs):
    print(expr_tree)


def dump_in_file(expr_tree: CfgTree, dump_dir: Path):
    path_exists(dump_dir)
    with open(dump_dir, "w") as dd:
        dd.write(str(expr_tree))


def main(cfg_dir: Path, dump_dir: Path, dump_func: Callable, yaml_load_func: Callable):
    cfg_dict = load_as_dict(cfg_dir, yaml_load_func)
    expr_tree = dict_to_expr_tree(cfg_dict)
    dump_func(expr_tree, dump_dir)


if __name__ == "__main__":
    pass
