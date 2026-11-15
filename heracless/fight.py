"""Loading YAML configs as typed dataclasses.

All the work (YAML parsing, type inference, stub generation and building the
dataclass objects) happens in the Rust extension ``heracless._core``; this module
only normalises arguments.
"""

from pathlib import Path
from typing import Any

from heracless import _core
from heracless.utils.exceptions import DirectoryError


def _stub_path(file_path: Path | str) -> Path:
    """Stubs always get a ``.pyi`` suffix, so passing ``Path(__file__)`` of the loader module works."""
    path = Path(file_path)
    if path.suffix != ".pyi":
        path = path.with_suffix(".pyi")
    if not path.parent.is_dir():
        raise DirectoryError(path.parent)
    return path


def load_config(config_path: Path | str, file_path: Path | str | None = None, frozen: bool = True) -> Any:
    """
    Load a YAML config file as a (nested) dataclass instance.

    :param config_path: Path to the YAML configuration file.
    :param file_path: Where to write the ``.pyi`` type stub (its suffix is replaced by ``.pyi``).
        Pass ``None`` to skip stub generation.
    :param frozen: Whether the generated dataclasses are immutable.
    :return: The config object, or ``None`` if the file is empty.
    :raises DirectoryError: If the config file (a ``FileNotFoundError``) or the stub's directory doesn't exist.
    :raises YamlSyntaxError: If the file is not valid YAML.
    :raises ConfigError: If the YAML's top level is not a mapping.
    """
    if config_path is None:
        raise TypeError("config_path cannot be None, please pass the path to your config file")
    stub_path = _stub_path(file_path) if file_path is not None else None
    return _core.load_config(Path(config_path), frozen, stub_path)


def fight(cfg_dir: Path | str, dump_dir: Path | str | None = None, frozen: bool = True) -> Any:
    """Alias of :func:`load_config` with the historical parameter names."""
    return load_config(cfg_dir, dump_dir, frozen)


def generate_stub(config_path: Path | str, frozen: bool = True) -> str | None:
    """Return the type stub for a config file without loading it into objects (``None`` if empty)."""
    return _core.generate_stub(Path(config_path), frozen)


def load_as_dict(cfg_dir: Path | str) -> Any:
    """Parse a YAML file into plain dicts and lists (``None`` if the file is empty)."""
    return _core.load_yaml(Path(cfg_dir))
