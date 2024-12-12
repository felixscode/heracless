from pathlib import Path

from heracless.utils import as_dict, from_dict, mutate_config
from heracless.fight import fight as load_config

if __name__ == "__main__":
    cfg_path = Path("./heracless/tests/test_config.yaml")
    dump_dir = Path("./heracless/tests/conftest.py")

    config = load_config(cfg_path=cfg_path, dump_dir=dump_dir)
    print(config)
    _dict = as_dict(config)
    _config = from_dict(_dict)
    config = mutate_config(config, "invoice", 0)
    assert config.invoice == 0
