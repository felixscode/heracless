import os
from pathlib import Path

from heracless.utils.exceptions import DirectoryError


def path_exists(path: Path):
    if not path.parent.exists():
        raise DirectoryError(f"Directory {path.parent} does not exist")
    if not path.exists():
        path.touch()


def insert_path_into_load_config_template(config_dir: Path) -> list[str]:
    """
    Inserts the path of the config file into the load_config function template
    """
    _mod_lines = []
    template_path = Path(__file__).parent / "load_func_template.py"
    with open(template_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("CONFIG_YAML_PATH ="):
                _mod_lines.append(f'CONFIG_YAML_PATH = Path("{config_dir}")')
            else:
                _mod_lines.append(line)
    return _mod_lines


def dump_template_to_file(config_path: Path, file_path: Path, force: bool = False):
    if not force and os.path.exists(file_path):
        return
    lines = insert_path_into_load_config_template(config_path)
    with open(file_path, "w") as f:
        for line in lines:
            f.write(line)
