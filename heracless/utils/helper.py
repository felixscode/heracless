from dataclasses import asdict, fields, is_dataclass, replace
from typing import Any, TypeVar

from heracless import _core

_T = TypeVar("_T")


def mutate_config(config: _T, name: str, value: Any) -> _T:
    """
    Return a copy of ``config`` with the attribute at ``name`` replaced by ``value``.

    Works on frozen configs; the original is left untouched.

    :param config: A config object.
    :param name: Dot-separated attribute path, e.g. ``"database.port"``.
    :param value: The new value.
    :return: A new config object.
    :raises AttributeError: If ``name`` doesn't refer to an existing field.
    """
    head, _, rest = name.partition(".")
    if not is_dataclass(config) or isinstance(config, type):
        raise TypeError(f"mutate_config() expects a config object, got {type(config).__name__}")
    if head not in {f.name for f in fields(config)}:
        raise AttributeError(f"{type(config).__name__} has no field {head!r}")
    new_value = mutate_config(getattr(config, head), rest, value) if rest else value
    return replace(config, **{head: new_value})


def as_dict(config: Any) -> dict[str, Any]:
    """
    Convert a config object to nested dicts (lists stay tuples).

    :param config: A config object.
    :return: A dict representation of ``config``.
    """
    return asdict(config)


def from_dict(config_dict: dict[Any, Any], frozen: bool = True) -> Any:
    """
    Build a config object from a dict, inferring the types the same way as for YAML files.

    :param config_dict: A dict representing the configuration.
    :param frozen: Whether the config object is immutable (default: ``True``).
    :return: A config object.
    """
    return _core.from_dict(config_dict, frozen)
