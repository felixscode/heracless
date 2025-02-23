from pathlib import Path
from typing import TypeVar

from heracless import load_config as _load_config

# CONFIG_YAML_PATH is a global variable that sets the path of your yaml config file
# Edit this to your config file path
CONFIG_YAML_PATH = None

Config = TypeVar("Config")


def load_config(config_path : Path|str = CONFIG_YAML_PATH,frozen: bool = True,stub_dump:bool = True) -> Config:
    """
    Load the configuration from the specified directory and return a Config object.

    Args:
        config_path (Path|str, optional): The path to the configuration file. Defaults to CONFIG_YAML_PATH.
        frozen (bool, optional): Whether the configuration should be frozen. Defaults to True.
        stub_dump (bool, optional): Whether to dump a stub file for typing support or not. Defaults to True.

    Returns:
        Config: The loaded configuration object.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML configuration file.

    Note:
        CONFIG_YAML_PATH is a global variable that sets the path of your YAML config file.
    """

    file_path = Path(__file__).resolve() if stub_dump else None
    return _load_config(config_path, file_path, frozen=frozen)
