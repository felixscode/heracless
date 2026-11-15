"""Heracless: type-safe YAML configuration for Python, powered by a Rust core."""

from importlib.metadata import PackageNotFoundError, version

from heracless.fight import generate_stub, load_config
from heracless.utils.exceptions import ConfigError, DirectoryError, HeraclessError, YamlSyntaxError
from heracless.utils.helper import as_dict, from_dict, mutate_config

try:
    __version__ = version("heracless")
except PackageNotFoundError:  # pragma: no cover - running from a source tree without metadata
    __version__ = "unknown"

__all__ = [
    "ConfigError",
    "DirectoryError",
    "HeraclessError",
    "YamlSyntaxError",
    "as_dict",
    "from_dict",
    "generate_stub",
    "load_config",
    "mutate_config",
]
