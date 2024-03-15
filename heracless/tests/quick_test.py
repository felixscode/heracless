from heracless import heracless, as_dict, from_dict, load_config, mutate_config
from pathlib import Path


if __name__ == "__main__":
    cfg_path = Path("./heracless/tests/test_config.yaml")
    dump_dir = Path("./heracless/tests/conftest.py")

    config = load_config(cfg_path=cfg_path, dump_dir=dump_dir)
    _dict = as_dict(config)
    _config = from_dict(_dict)
    config = mutate_config(config, "invoice", 0)
    assert config.invoice == 0
