from pathlib import Path
from typing import Callable, TypeAlias

from yaml import full_load
from heracless.utils.c_types import Config
from heracless.main import DEFAULT_DIR, DEFAULT_DUMP_DIR, dump_in_file, main
from pathlib import Path
from typing import Callable, TypeAlias
from yaml import full_load
from heracless.utils.c_types import Config
from heracless.main import DEFAULT_DIR, DEFAULT_DUMP_DIR, dump_in_file, main


def heracless(
    cfg_path: Path = DEFAULT_DIR,
    dump_func: Callable = dump_in_file,
    dump_dir: Path = DEFAULT_DUMP_DIR,
    make_dir: bool = True,
    frozen: bool = True,
) -> Config:
    """
    A decorator that provides a config object as the first argument to the decorated function.

    Args:
        cfg_path (Path): The directory where the config YAML file is located. Defaults to DEFAULT_DIR.
        dump_func (Callable): The function that controls the dump behavior. Defaults to dump_in_file.
        dump_dir (Path): The directory for generated typing files. Defaults to DEFAULT_DUMP_DIR.
        make_dir (bool): Flag to indicate whether to create the directory if it doesn't exist. Defaults to True.
        frozen (bool): Flag to indicate whether the config object should be frozen. Defaults to True.

    Returns:
        Config: The config object.

    Usage:
        Add @heracless() as a decorator on top of functions. It will provide a config object as the first argument to your target function.

        @heracless()
        def target_function(config: Config, *args, **kwargs):
            pass
    """

    def heracless_wrapper(func):
        def _fight_hydra(*args, **kwargs):
            cfg = main(
                cfg_dir=cfg_path,
                dump_dir=dump_dir,
                dump_func=dump_func,
                yaml_load_func=full_load,
                make_dir=make_dir,
                frozen=frozen,
            )
            output = func(cfg, *args, **kwargs)
            return output

        return _fight_hydra

    return heracless_wrapper
