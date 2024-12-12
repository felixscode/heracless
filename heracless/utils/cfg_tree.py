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

"""
contains domain logic for config handling:
constructs a meta obj tree: used to construct config obj and generate typing files
"""


IMPORTS: str = (
    "from dataclasses import dataclass\nfrom datetime import datetime\nfrom datetime import date\nfrom pathlib import Path"
)
FUNCTION_STUB: str = "\ndef load_config(config_path: str) -> Config: ..."
# type aliases to avoid redundancy in type annotations
Node: TypeAlias = Union["Leaf", "Structure"]
Value: TypeAlias = Any


# helper_functions for string conversions
def replace_invalid_names(name: str) -> str:
    """
    Replace invalid characters in a name with underscores.

    Args:
        name (str): The name to be sanitized.

    Returns:
        str: The sanitized name with invalid characters replaced by underscores.
    """
    return re.sub("[^a-zA-Z0-9 \n\.]", "_", name)


def as_uppercase(name: str) -> str:
    """
    Convert a name to uppercase.

    Args:
        name (str): The name to be converted.

    Returns:
        str: The name converted to uppercase.
    """
    name = as_lowercase(name)  # add _ incase its already uppercase
    return "".join(word.title() for word in name.split("_"))


def as_lowercase(name: str) -> str:
    """
    Convert a name to lowercase.

    Args:
        name (str): The name to be converted.

    Returns:
        str: The name converted to lowercase.
    """
    name = replace_invalid_names(name)
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def format_str(input: str) -> str:
    """
    Format a string using black.

    Args:
        input (str): The string to be formatted.

    Returns:
        str: The formatted string.
    """
    return black.format_str(input, mode=black.Mode())


# meta type definitions

Leaf = namedtuple("Leaf", ("name", "type", "value"))
Structure = namedtuple("Structure", ("name", "type", "children"))
Tree = namedtuple("Tree", ("name", "children"))


# tree builder
def iterable_generator(value: Any, name: str) -> Iterable:
    """
    Generate an iterable from a value.

    Args:
        value (Any): The value to be converted into an iterable.
        name (str): The name associated with the value.

    Returns:
        Iterable: An iterable representation of the value.

    Raises:
        NotIterable: If the value is not iterable.
    """
    match value:
        case dict():
            return value.items()
        case list():  # tuples are preferred in dataclasses (mutability)
            return zip(repeat(name + "_item"), tuple(value))
        case tuple() | set():
            return zip(repeat(name + "_item"), value)
        case _:
            raise NotIterable(value)


def iterable_to_type_mapper(name: str, value: Value) -> tuple[Type[Node], str, Value]:
    """
    Map an iterable to its corresponding node type.

    Args:
        name (str): The name associated with the value.
        value (Value): The value to be mapped.

    Returns:
        tuple[Type[Node], str, Value]: A tuple containing the node type, name, and value.
    """
    if isinstance(value, Iterable) and not isinstance(value, (str, Path, date, datetime)):
        return Structure, name, value
    return Leaf, name, value


def tree_builder(obj_type: Type[Node], name: str, value: Union[Value, Iterable]) -> Node:
    """
    Build a tree of nodes from a value.

    Args:
        obj_type (Type[Node]): The type of the node (Leaf or Structure).
        name (str): The name associated with the value.
        value (Union[Value, Iterable]): The value to be converted into a tree.

    Returns:
        Node: The root node of the constructed tree.
    """
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
    """
    Generate the class heading for a structure.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        structure (Structure): The structure for which the class heading is generated.

    Returns:
        str: The generated class heading.
    """
    return f"""\n@dataclass(frozen={frozen})\nclass {as_uppercase(structure.name)}:\n"""


def structure_class_entry_generator(structure: Structure) -> str:
    """
    Generate the class entry for a structure.

    Args:
        structure (Structure): The structure for which the class entry is generated.

    Returns:
        str: The generated class entry.
    """
    return f"""\t{as_lowercase(structure.name)}: "{as_uppercase(structure.name)}"\n"""


def leaf_class_entry_generator(leaf: Leaf) -> str:
    """
    Generate the class entry for a leaf.

    Args:
        leaf (Leaf): The leaf for which the class entry is generated.

    Returns:
        str: The generated class entry.
    """
    return f"""\t{as_lowercase(leaf.name)}: {leaf.type}\n"""


def child_type_mapper(child: Node) -> str:
    """
    Map the child type to its corresponding string representation.

    Args:
        child (Node): The child node to be mapped.

    Returns:
        str: The string representation of the child type.
    """
    match child, child.type:
        case Structure(), "dict":
            return f""" "{as_uppercase(child.name)}" """
        case Structure(), _:
            return f"""{child.type}[{child_type_mapper(child.children[0])}]"""  # recursion if nested list tuple or set
        case _:
            return child.type


def non_dict_structure_entry_generator(structure: Structure) -> str:
    """
    Generate the entry for a non-dict structure.

    Args:
        structure (Structure): The structure for which the entry is generated.

    Returns:
        str: The generated entry.
    """
    return f"""\t{structure.name}: {structure.type}[{child_type_mapper(structure.children[0])}]\n"""


def entry_generator_mapping(node: Node) -> callable:
    """
    Map a node to its corresponding entry generator function.

    Args:
        node (Node): The node to be mapped.

    Returns:
        callable: The entry generator function for the node.
    """
    match (node, node.type):
        case (Leaf(), _):
            return leaf_class_entry_generator
        case (Structure(), "dict"):
            return structure_class_entry_generator
        case _:
            return non_dict_structure_entry_generator


def structure_to_str_generator(frozen: bool, structure: Structure) -> str:
    """
    Generate the string representation of a structure.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        structure (Structure): The structure to be converted to a string.

    Returns:
        str: The string representation of the structure.
    """
    class_heading = class_heading_generator(frozen, structure)
    child_entry_functions = map(entry_generator_mapping, structure.children)
    zipped_child_functions = zip(child_entry_functions, structure.children)
    entries = reduce(lambda a, b: a + b, (func(elem) for func, elem in zipped_child_functions))
    return class_heading + entries


def tree_iterator(tree: Union[Tree, Structure]) -> Iterator[Structure]:
    """
    Iterate over the structures in a tree.

    Args:
        tree (Union[Tree, Structure]): The tree to be iterated over.

    Yields:
        Iterator[Structure]: An iterator over the structures in the tree.
    """
    if type(tree) == Tree:
        yield tree
    elif tree.type == "dict":
        yield tree

    filtered_structures = tuple(filter(lambda child: type(child) == Structure, tree.children))
    yield from (elem for child in filtered_structures for elem in (tree_iterator(child)))


def tree_to_str_generator(frozen: bool, tree: Tree) -> str:
    """
    Generate the string representation of a tree.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        tree (Tree): The tree to be converted to a string.

    Returns:
        str: The string representation of the tree.
    """
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
    """
    Translate a tree to a string representation.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        tree (Tree): The tree to be translated.

    Returns:
        str: The string representation of the tree.
    """
    import_str = IMPORTS
    raw_str = tree_to_str_generator(frozen, tree)
    function_str = FUNCTION_STUB
    return format_str(import_str + raw_str + function_str)


# dynamic dataclass generation


def leaf_attribute_mapper(leaf: Leaf) -> Value:
    """
    Map a leaf to its corresponding attribute.

    Args:
        leaf (Leaf): The leaf to be mapped.

    Returns:
        Value: The value of the leaf.
    """
    return leaf.value


def non_dict_structure_mapper(frozen: bool, child: Node) -> Iterable[Value | Node]:
    """
    Map a non-dict structure to its corresponding attributes.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        child (Node): The child node to be mapped.

    Returns:
        Iterable[Value | Node]: An iterable of the mapped attributes.
    """
    return getattr(builtins, child.type)((attribute_generation_function_mapper(frozen, c)[1] for c in child.children))


def attribute_generation_function_mapper(frozen: bool, child: Node) -> tuple[str, Any]:
    """
    Map a child node to its corresponding attribute generation function.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        child (Node): The child node to be mapped.

    Returns:
        tuple[str, Any]: A tuple containing the attribute name and value.
    """
    match (child, child.type):
        case (Leaf(), _):
            return as_lowercase(child.name), leaf_attribute_mapper(child)
        case (Structure(), "dict"):
            return as_lowercase(child.name), tree_to_config_obj(frozen, child)
        case (Structure(), _):
            return as_lowercase(child.name), non_dict_structure_mapper(frozen, child)


def tree_to_config_obj(frozen: bool, tree: Union[Tree, Structure]) -> Any:
    """
    Generate a config object from a tree.

    Args:
        frozen (bool): Whether the dataclass should be frozen.
        tree (Union[Tree, Structure]): The tree to be converted to a config object.

    Returns:
        Any: The generated config object.
    """
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
    """
    Parse a dictionary and build a tree.

    Args:
        _dict (dict): The dictionary to be parsed.

    Returns:
        Tree: The root node of the constructed tree.
    """
    tree = tree_builder(Tree, "Config", _dict)
    return tree


if __name__ == "__main__":
    pass
