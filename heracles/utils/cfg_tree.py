from abc import abstractmethod
from typing import Union, TypeAlias, Self, Any
import re
import black

IMPORTS = "from dataclasses import dataclass\nfrom datetime import datetime\nfrom datetime import date\nfrom pathlib import Path"

CfgTreeNode: TypeAlias = Union["CfgLeaf", "CfgStruct"]
CfgTree: TypeAlias = "CfgStruct"


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
    def __init__(self, name, value, children, frozen) -> None:
        super().__init__(name, value, CfgStruct)
        self.children = children
        self.frozen = frozen

    @abstractmethod
    def is_self(key: str, value: Any):
        if type(value) in (dict,):
            return True
        return False

    @abstractmethod
    def from_dict(name, cfg_dict, frozen):
        children = tuple()
        for key, value in cfg_dict.items():
            if CfgStruct.is_self(key, value):
                children += (CfgStruct.from_dict(key, value, frozen=frozen),)
            else:
                children += (CfgLeaf(key, value),)
        return CfgStruct(name=name, value=value, children=children, frozen=frozen)

    def get_str_information(self) -> str:
        return f"   {as_lowercase(self.name)}:{as_uppercase(self.name)}"

    def get_children_str_information(self):
        output_str = ""
        for child in self.children:

            output_str += "\n"
            output_str += child.get_str_information()
        return output_str

    def to_obj(self):
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
                return_str += str(child)

        return_str += f"""\n@dataclass(frozen={self.frozen})\nclass {as_uppercase(self.name)}:\n{self.get_children_str_information()}"""
        if self.name == "config":
            imports = IMPORTS
            return format_str(imports + return_str)
        return return_str


class CfgLeaf(CfgNode):
    def __init__(self, name: str, value: Any) -> None:
        super().__init__(name, value, type(value))
        self.value = value

    def get_str_information(self):
        return str(self)

    def to_obj(self):
        return self.name, self.value

    def __str__(self):
        return f"   {self.name}:{str(self.type.__name__)}"


def dict_to_cfg_tree(cfg_dict: dict, frozen=True) -> CfgTree:
    cfg_tree = CfgStruct.from_dict("config", cfg_dict, frozen=frozen)
    return cfg_tree
