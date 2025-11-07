from pathlib import Path
from typing import Any, Optional

from heracless import load_config as _load_config

CONFIG_YAML_PATH: Optional[Path] = None
# CONFIG_YAML_PATH is a global variable that sets the path of your yaml config file
# Edit this to your config file path


def load_config(config_path: Optional[Path | str] = None, frozen: bool = True, stub_dump: bool = True) -> Any:
    """
    Load the configuration from the specified directory and return a Config object.

    Args:
        config_path (Path|str, optional): The path to the configuration file. Defaults to CONFIG_YAML_PATH.
        frozen (bool, optional): Whether the configuration should be frozen. Defaults to True.
        stub_dump (bool, optional): Whether to dump a stub file for typing support or not. Defaults to True.

    Returns:
        Any: The loaded configuration object.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML configuration file.

    Note:
        CONFIG_YAML_PATH is a global variable that sets the path of your YAML config file.
    """
    if config_path is None:
        config_path = CONFIG_YAML_PATH
    if config_path is None:
        raise ValueError("config_path must be specified either as argument or via CONFIG_YAML_PATH")
    file_path: Optional[Path] = Path(__file__).resolve() if stub_dump else None
    return _load_config(config_path, file_path, frozen=frozen)
