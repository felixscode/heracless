from dataclasses import asdict, replace
from typing import Any, TypeVar

import heracless.utils as _heracless_utils

Config = TypeVar("Config")


def mutate_config(config: Config, name: str, value: Any) -> Config:
    """
    mutate_config: a function that takes a config, a name and a value and returns a new config with the value at the name
    args:
        config: a Config object representing the configuration
        name: a string representing the name of the value to be changed
        value: the value to be changed
    returns:
        Config: a new Config object with the updated value
    """
    name_list = name.split(".")
    if len(name_list) == 1:
        return replace(config, **{name: value})
    else:
        return replace(
            config,
            **{name_list[0]: mutate_config(getattr(config, name_list[0]), ".".join(name_list[1:]), value)},
        )


def as_dict(config: Config) -> dict:
    """
    as_dict: a function that converts a Config object to a dictionary
    args:
        config: a Config object representing the configuration
    returns:
        dict: a dictionary representation of the Config object
    """
    return asdict(config)


def from_dict(config_dict: dict, frozen: bool = True) -> Config:
    """
    from_dict: a function that creates a Config object from a dictionary
    args:
        config_dict: a dictionary representing the configuration
        frozen: a boolean indicating whether the Config object should be frozen (default: True)
    returns:
        Config: a Config object created from the dictionary
    """
    return _heracless_utils.cfg_tree.tree_to_config_obj(frozen, _heracless_utils.cfg_tree.tree_parser(config_dict))
