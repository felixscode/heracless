from pathlib import Path
from typing import Callable, TypeAlias

from yaml import full_load

from heracless.main import DEFAULT_DIR, DEFAULT_DUMP_DIR, dump_in_file, main

Config: TypeAlias = "Config"


def heracless(
    cfg_path: Path = DEFAULT_DIR,
    dump_func: Callable = dump_in_file,
    dump_dir: Path = DEFAULT_DUMP_DIR,
    make_dir: bool = True,
    frozen: bool = True,
) -> Config:
    """
    heracless decorator:
    args: cfg_path directory where config yaml location, dump_func: controls dump behavior, dump_dir: directory for generated typing files
    return: config obj
    usage: add @heracless() as decorator on top of functions, its gonna provide a config obj as first argument into your target func:
    @heracless()
    def target_function(config:Config,*args,**kwargs):
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
