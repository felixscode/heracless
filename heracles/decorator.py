from heracles.main import dump_in_file, main, DEFAULT_DIR, DEFAULT_DUMP_DIR
from yaml import full_load


def heracles(cfg_dir=DEFAULT_DIR, dump_func=dump_in_file, dump_dir=DEFAULT_DUMP_DIR):
    def heracles_wrapper(func):
        def _fight_hydra(*args, **kwargs):
            _, cfg = main(
                cfg_dir=cfg_dir,
                dump_dir=dump_dir,
                dump_func=dump_func,
                yaml_load_func=full_load,
            )
            output = func(cfg, *args, **kwargs)
            return output

        return _fight_hydra

    return heracles_wrapper
