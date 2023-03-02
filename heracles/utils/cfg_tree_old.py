"""
conatains domain locic for config handling:
constucts a meta obj tree: used to construct config obj and gerneate typing files
"""

from abc import abstractmethod
from typing import Union, TypeAlias, Self, Any, Type, Iterator
import re
import black

IMPORTS = "from dataclasses import dataclass\nfrom datetime import datetime\nfrom datetime import date\nfrom pathlib import Path"

TreeNode: TypeAlias = Union["CfgLeaf", "CfgStruct"]
Tree: TypeAlias = "CfgStruct"


def replace_unvalid_names(name):
    return re.sub("[^a-zA-Z0-9 \n\.]", "_", name)


def as_uppercase(name: str) -> str:
    name = replace_unvalid_names(name)
    return "".join(word.title() for word in name.split("_"))


def as_lowercase(name: str) -> str:
    name = replace_unvalid_names(name)
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def format_str(input: str) -> str:
    return black.format_str(input, mode=black.Mode())


class CfgNode:
    def __init__(self, name, value, type) -> None:
        self.name = name
        self.type = type


class CfgStruct(CfgNode):
    """
    config struct meta ob. represents a strucktural obj within the config tree
    """

    def __init__(self, name, value, children, frozen) -> None:
        super().__init__(name, value, CfgStruct)
        self.children = children
        self.frozen = frozen

    @abstractmethod
    def is_self(key: str, value: Any) -> bool:
        """
        checks if a dict value is a dict again: means value is a substrctur and can be translated into a CfgStruct again
        """
        if type(value) in (dict,):
            return True
        return False

    def get_str_information(self) -> str:
        return f"   {as_lowercase(self.name)}:{as_uppercase(self.name)}"

    def get_children_str_information(self):
        output_str = ""
        for child in self.children:

            output_str += "\n"
            output_str += child.get_str_information()
        return output_str

    def to_obj(self) -> tuple[str, Type]:
        child_obj = tuple()
        for child in self.children:
            child_obj += (child.to_obj(),)
        attr_dict = {
            name: obj for name, obj in child_obj
        }  # map tuple of objects to dict where key is obj name and value obj it self
        return as_lowercase(self.name), type(as_uppercase(self.name), (), attr_dict)

    def __str__(self):
        return_str = ""
        for child in self.children:
            if type(child) == CfgStruct:
                child_string = str(child)
                return_str += (
                    child_string if child_string not in return_str else ""
                )  # if statement prevents duplicates

        return_str += f"""\n@dataclass(frozen={self.frozen})\nclass {as_uppercase(self.name)}:\n{self.get_children_str_information()}"""
        if self.name == "config":
            return format_str(
                IMPORTS + return_str
            )  # alogo goes bottom to top of tree if config wer at top.. so imports get added and str gets formatted
        return return_str


class CfgLeaf(CfgNode):
    """
    Leaf meta class represents acctual value within the config structur
    """

    def __init__(self, name: str, value: Any) -> None:
        super().__init__(name, value, type(value))
        self.value = value

    def get_str_information(self) -> str:
        return str(self)

    def to_obj(self) -> tuple[str, Type]:
        return self.name, self.value

    def __str__(self):
        return f"   {self.name}:{str(self.type.__name__)}"


def dict_to_cfg_tree(cfg_dict: dict, frozen=True) -> Tree:
    cfg_tree = CfgStruct.from_dict("meta_root", cfg_dict, frozen=frozen)
    return cfg_tree
