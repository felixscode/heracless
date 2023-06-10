"""
contains domain logic for config handling:
constructs a meta obj tree: used to construct config obj and generate typing files
"""

import builtins
import re
from collections import namedtuple
from dataclasses import make_dataclass
from datetime import date, datetime
from functools import *
from itertools import repeat
from pathlib import Path
from typing import Any, Iterable, Iterator, Type, TypeAlias, Union

import black

from heracless.utils.exceptions import NotIterable

IMPORTS = "from dataclasses import dataclass\nfrom datetime import datetime\nfrom datetime import date\nfrom pathlib import Path"

# type aliases to avoid redundancy in type annotations
Node: TypeAlias = Union["Leaf", "Structure"]
Value: TypeAlias = Any
Config: TypeAlias = object


# helper_functions for string conversions
def replace_invalid_names(name):
    return re.sub("[^a-zA-Z0-9 \n\.]", "_", name)


def as_uppercase(name: str) -> str:
    name = as_lowercase(name)  # add _ incase its allready uppercase
    return "".join(word.title() for word in name.split("_"))


def as_lowercase(name: str) -> str:
    name = replace_invalid_names(name)
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def format_str(input: str) -> str:
    return black.format_str(input, mode=black.Mode())


# meta type definitions

Leaf = namedtuple("Leaf", ("name", "type", "value"))
Structure = namedtuple("Structure", ("name", "type", "children"))
Tree = namedtuple("Tree", ("name", "children"))


# tree builder
def iterable_generator(value: Any, name: str) -> Iterable:
    match value:
        case dict():
            return value.items()
        case list():  # tuples are preferred in dataclasses (mutabilty)
            return zip(repeat(name + "_item"), tuple(value))
        case tuple() | set():
            return zip(repeat(name + "_item"), value)
        case _:
            raise NotIterable(value)


def iterable_to_type_mapper(name: str, value: Value) -> tuple[Node, str, Value]:
    if isinstance(value, Iterable) and not isinstance(value, (str, Path, date, datetime)):
        return Structure, name, value
    return Leaf, name, value


def tree_builder(obj_type: Type[Node], name: str, value: Union[Value, Iterable]) -> Iterable[Node]:
    if obj_type == Leaf:  # base case
        return obj_type(name, type(value).__name__, value)

    iterables = iterable_generator(value, name)
    type_value_name_elements = map(iterable_to_type_mapper, *zip(*iterables))
    children = map(tree_builder, *zip(*type_value_name_elements))
    if obj_type == Tree:
        return obj_type(name, tuple(children))
    if type(value) == list:  # dataclasses don't like lists
        return obj_type(name, "tuple", tuple(children))
    return obj_type(name, type(value).__name__, tuple(children))


# string generator


def class_heading_generator(frozen: bool, structure: Structure) -> str:
    return f"""\n@dataclass(frozen={frozen})\nclass {as_uppercase(structure.name)}:\n"""


def structure_class_entry_generator(structure: Structure) -> str:
    return f"""\t{as_lowercase(structure.name)}:"{as_uppercase(structure.name)}"\n"""


def leaf_class_entry_generator(leaf: Leaf) -> str:
    return f"""\t{as_lowercase(leaf.name)}:{leaf.type}\n"""


def child_type_mapper(child: Node):
    match child, child.type:
        case Structure(), "dict":
            return f""" "{as_uppercase(child.name)}" """
        case Structure(), _:
            return f"""{child.type}[{child_type_mapper(child.children[0])}]"""  # recursion if nested list tuple or set
        case _:
            return child.type


def non_dict_structure_entry_generator(structure: Structure) -> Structure:
    return f"""\t{structure.name}:{structure.type}[{child_type_mapper(structure.children[0])}]\n"""


def entry_generator_mapping(node: Node) -> callable:
    match (node, node.type):
        case (Leaf(), _):
            return leaf_class_entry_generator
        case (Structure(), "dict"):
            return structure_class_entry_generator
        case _:
            return non_dict_structure_entry_generator


def structure_to_str_generator(frozen, structure: Structure) -> str:
    class_heading = class_heading_generator(frozen, structure)
    child_entry_functions = map(entry_generator_mapping, structure.children)
    zipped_child_functions = zip(child_entry_functions, structure.children)
    entries = reduce(lambda a, b: a + b, (func(elem) for func, elem in zipped_child_functions))
    return class_heading + entries


def tree_iterator(tree: Union[Tree, Structure]) -> Iterator[Structure]:
    if type(tree) == Tree:
        yield tree
    elif tree.type == "dict":
        yield tree

    filtered_structures = tuple(filter(lambda child: type(child) == Structure, tree.children))
    yield from (elem for child in filtered_structures for elem in (tree_iterator(child)))


def tree_to_str_generator(frozen: bool, tree: Tree) -> str:
    structure_children = tree_iterator(tree)
    strings = tuple(
        reversed(
            tuple(
                map(partial(structure_to_str_generator, frozen), structure_children)
            )  # reversing to have right order in file
        )
    )
    filtered_strings = tuple(set(strings))  # filters duplicated strings
    return "".join(filtered_strings)


def tree_to_string_translator(
    frozen: bool,
    tree: Tree,
) -> str:
    import_str = IMPORTS
    raw_str = tree_to_str_generator(frozen, tree)
    return format_str(import_str + raw_str)


# dynamic dataclass generation


def leaf_attribute_mapper(leaf: Leaf) -> tuple[str, Value]:
    return leaf.value


def non_dict_structure_mapper(frozen: bool, child: Node) -> Iterable[Value | Node]:
    return getattr(builtins, child.type)((attribute_generation_function_mapper(frozen, c)[1] for c in child.children))


def attribute_generation_function_mapper(frozen: bool, child: Node):
    match (child, child.type):
        case (Leaf(), _):
            return as_lowercase(child.name), leaf_attribute_mapper(child)
        case (Structure(), "dict"):
            return as_lowercase(child.name), tree_to_config_obj(frozen, child)
        case (Structure(), _):
            return as_lowercase(child.name), non_dict_structure_mapper(frozen, child)


def tree_to_config_obj(frozen: bool, tree: Union[Tree, Structure]) -> Config:
    name = as_uppercase(tree.name)
    attrs_dict = tuple((attribute_generation_function_mapper(frozen, child) for child in tree.children))
    dclass = make_dataclass(
        name,
        ((entry[0], type(entry[1]), entry[1]) for entry in attrs_dict),
        frozen=True,
    )
    return dclass()


# parse dict
def tree_parser(_dict: dict) -> Tree:
    tree = tree_builder(Tree, "Config", _dict)
    return tree


if __name__ == "__main__":
    pass
