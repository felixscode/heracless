"""
Comprehensive tests for heracless.utils.cfg_tree module
"""

from datetime import date, datetime
from pathlib import Path

import pytest

from heracless.utils.cfg_tree import (
    Leaf,
    Structure,
    Tree,
    as_lowercase,
    as_uppercase,
    attribute_generation_function_mapper,
    child_type_mapper,
    class_heading_generator,
    entry_generator_mapping,
    format_str,
    iterable_generator,
    iterable_to_type_mapper,
    leaf_attribute_mapper,
    leaf_class_entry_generator,
    non_dict_structure_entry_generator,
    non_dict_structure_mapper,
    replace_invalid_names,
    structure_class_entry_generator,
    structure_to_str_generator,
    tree_builder,
    tree_iterator,
    tree_parser,
    tree_to_config_obj,
    tree_to_str_generator,
    tree_to_string_translator,
)
from heracless.utils.exceptions import NotIterable


class TestStringHelpers:
    """Test string manipulation helper functions"""

    def test_replace_invalid_names_basic(self) -> None:
        assert replace_invalid_names("test-name") == "test_name"
        assert replace_invalid_names("test@name") == "test_name"
        assert replace_invalid_names("test#name$") == "test_name_"

    def test_replace_invalid_names_special_chars(self) -> None:
        assert replace_invalid_names("a!b@c#d$e%f") == "a_b_c_d_e_f"
        assert replace_invalid_names("test-123_abc.xyz") == "test_123_abc_xyz"

    def test_as_uppercase_simple(self) -> None:
        assert as_uppercase("test") == "Test"
        assert as_uppercase("test_name") == "TestName"
        assert as_uppercase("test_long_name") == "TestLongName"

    def test_as_uppercase_with_hyphen(self) -> None:
        assert as_uppercase("test-name") == "TestName"
        assert as_uppercase("some-test-name") == "SomeTestName"

    def test_as_lowercase_simple(self) -> None:
        assert as_lowercase("Test") == "test"
        assert as_lowercase("TestName") == "test_name"
        assert as_lowercase("TestLongName") == "test_long_name"

    def test_as_lowercase_with_special_chars(self) -> None:
        assert as_lowercase("Test-Name") == "test_name"
        assert as_lowercase("Test@Name") == "test_name"

    def test_format_str_valid_code(self) -> None:
        """Test that format_str properly formats Python code"""
        input_code = "def foo(): pass"
        result = format_str(input_code)
        assert "def foo():" in result
        assert "pass" in result


class TestMetaTypes:
    """Test named tuple meta types"""

    def test_leaf_creation(self) -> None:
        leaf = Leaf("test", "int", 42)
        assert leaf.name == "test"
        assert leaf.type == "int"
        assert leaf.value == 42

    def test_structure_creation(self) -> None:
        child = Leaf("item", "str", "value")
        structure = Structure("test", "dict", (child,))
        assert structure.name == "test"
        assert structure.type == "dict"
        assert len(structure.children) == 1

    def test_tree_creation(self) -> None:
        child = Leaf("item", "str", "value")
        tree = Tree("Config", (child,))
        assert tree.name == "Config"
        assert len(tree.children) == 1


class TestIterableGeneration:
    """Test iterable generation functions"""

    def test_iterable_generator_dict(self) -> None:
        value = {"a": 1, "b": 2}
        result = tuple(iterable_generator(value, "test"))
        assert len(result) == 2
        assert ("a", 1) in result
        assert ("b", 2) in result

    def test_iterable_generator_list(self) -> None:
        value = [1, 2, 3]
        result = tuple(iterable_generator(value, "test"))
        assert len(result) == 3
        assert all(name == "test_item" for name, _ in result)
        assert tuple(val for _, val in result) == (1, 2, 3)

    def test_iterable_generator_tuple(self) -> None:
        value = (1, 2, 3)
        result = tuple(iterable_generator(value, "test"))
        assert len(result) == 3
        assert all(name == "test_item" for name, _ in result)

    def test_iterable_generator_set(self) -> None:
        value = {1, 2, 3}
        result = tuple(iterable_generator(value, "test"))
        assert len(result) == 3
        assert all(name == "test_item" for name, _ in result)

    def test_iterable_generator_non_iterable(self) -> None:
        with pytest.raises(NotIterable):
            tuple(iterable_generator(42, "test"))

    def test_iterable_generator_string_not_iterable(self) -> None:
        """Strings should not be treated as iterables"""
        with pytest.raises(NotIterable):
            tuple(iterable_generator("test", "name"))

    def test_iterable_to_type_mapper_structure(self) -> None:
        node_type, name, value = iterable_to_type_mapper("test", {"a": 1})
        assert node_type == Structure
        assert name == "test"
        assert value == {"a": 1}

    def test_iterable_to_type_mapper_leaf(self) -> None:
        node_type, name, value = iterable_to_type_mapper("test", 42)
        assert node_type == Leaf
        assert name == "test"
        assert value == 42

    def test_iterable_to_type_mapper_string_as_leaf(self) -> None:
        """Strings should be treated as leaf values"""
        node_type, name, value = iterable_to_type_mapper("test", "hello")
        assert node_type == Leaf
        assert value == "hello"

    def test_iterable_to_type_mapper_path_as_leaf(self) -> None:
        """Path objects should be treated as leaf values"""
        path_value = Path("/tmp/test")
        node_type, name, value = iterable_to_type_mapper("test", path_value)
        assert node_type == Leaf
        assert value == path_value

    def test_iterable_to_type_mapper_date_as_leaf(self) -> None:
        """Date objects should be treated as leaf values"""
        date_value = date(2024, 1, 1)
        node_type, name, value = iterable_to_type_mapper("test", date_value)
        assert node_type == Leaf
        assert value == date_value

    def test_iterable_to_type_mapper_datetime_as_leaf(self) -> None:
        """Datetime objects should be treated as leaf values"""
        dt_value = datetime(2024, 1, 1, 12, 0, 0)
        node_type, name, value = iterable_to_type_mapper("test", dt_value)
        assert node_type == Leaf
        assert value == dt_value


class TestTreeBuilder:
    """Test tree building functions"""

    def test_tree_builder_leaf(self) -> None:
        result = tree_builder(Leaf, "test", 42)
        assert isinstance(result, Leaf)
        assert result.name == "test"
        assert result.type == "int"
        assert result.value == 42

    def test_tree_builder_simple_dict(self) -> None:
        value = {"a": 1, "b": 2}
        result = tree_builder(Structure, "test", value)
        assert isinstance(result, Structure)
        assert result.name == "test"
        assert result.type == "dict"
        assert len(result.children) == 2

    def test_tree_builder_nested_dict(self) -> None:
        value = {"a": {"b": 1}}
        result = tree_builder(Structure, "test", value)
        assert isinstance(result, Structure)
        assert len(result.children) == 1
        child = result.children[0]
        assert isinstance(child, Structure)
        assert child.name == "a"

    def test_tree_builder_list(self) -> None:
        value = [1, 2, 3]
        result = tree_builder(Structure, "test", value)
        assert isinstance(result, Structure)
        assert result.name == "test"
        assert result.type == "tuple"  # lists are converted to tuples
        assert len(result.children) == 3

    def test_tree_builder_mixed_types(self) -> None:
        value = {"num": 42, "text": "hello", "items": [1, 2, 3]}
        result = tree_builder(Structure, "config", value)
        assert isinstance(result, Structure)
        assert len(result.children) == 3

    def test_tree_parser_simple(self) -> None:
        test_dict = {"a": 1, "b": 2}
        result = tree_parser(test_dict)
        assert isinstance(result, Tree)
        assert result.name == "Config"
        assert len(result.children) == 2

    def test_tree_parser_nested(self) -> None:
        test_dict = {"level1": {"level2": {"level3": "value"}}}
        result = tree_parser(test_dict)
        assert isinstance(result, Tree)
        assert result.name == "Config"


class TestStringGeneration:
    """Test string generation for stub files"""

    def test_class_heading_generator_frozen(self) -> None:
        structure = Structure("TestClass", "dict", ())
        result = class_heading_generator(True, structure)
        assert "@dataclass(frozen=True)" in result
        assert "class TestClass:" in result

    def test_class_heading_generator_not_frozen(self) -> None:
        structure = Structure("TestClass", "dict", ())
        result = class_heading_generator(False, structure)
        assert "@dataclass(frozen=False)" in result
        assert "class TestClass:" in result

    def test_leaf_class_entry_generator(self) -> None:
        leaf = Leaf("test_value", "int", 42)
        result = leaf_class_entry_generator(leaf)
        assert "test_value: int" in result

    def test_structure_class_entry_generator(self) -> None:
        child = Leaf("item", "str", "value")
        structure = Structure("test_struct", "dict", (child,))
        result = structure_class_entry_generator(structure)
        assert "test_struct:" in result
        assert "TestStruct" in result

    def test_non_dict_structure_entry_generator(self) -> None:
        child = Leaf("item", "int", 1)
        structure = Structure("items", "tuple", (child,))
        result = non_dict_structure_entry_generator(structure)
        assert "items:" in result
        assert "tuple" in result

    def test_child_type_mapper_dict(self) -> None:
        child = Leaf("item", "str", "value")
        structure = Structure("test", "dict", (child,))
        result = child_type_mapper(structure)
        assert "Test" in result

    def test_child_type_mapper_list(self) -> None:
        child = Leaf("item", "int", 1)
        structure = Structure("items", "list", (child,))
        result = child_type_mapper(structure)
        assert "list" in result
        assert "int" in result

    def test_entry_generator_mapping_leaf(self) -> None:
        leaf = Leaf("test", "int", 42)
        func = entry_generator_mapping(leaf)
        assert func == leaf_class_entry_generator

    def test_entry_generator_mapping_structure_dict(self) -> None:
        child = Leaf("item", "str", "value")
        structure = Structure("test", "dict", (child,))
        func = entry_generator_mapping(structure)
        assert func == structure_class_entry_generator

    def test_entry_generator_mapping_structure_non_dict(self) -> None:
        child = Leaf("item", "int", 1)
        structure = Structure("items", "tuple", (child,))
        func = entry_generator_mapping(structure)
        assert func == non_dict_structure_entry_generator


class TestTreeIteration:
    """Test tree iteration functions"""

    def test_tree_iterator_simple_tree(self) -> None:
        child = Leaf("item", "str", "value")
        tree = Tree("Config", (child,))
        result = list(tree_iterator(tree))
        assert len(result) >= 1
        assert tree in result

    def test_tree_iterator_nested_structures(self) -> None:
        inner_child = Leaf("value", "int", 42)
        inner_struct = Structure("inner", "dict", (inner_child,))
        outer_struct = Structure("outer", "dict", (inner_struct,))
        tree = Tree("Config", (outer_struct,))
        result = list(tree_iterator(tree))
        assert tree in result
        assert outer_struct in result
        assert inner_struct in result


class TestConfigObjectGeneration:
    """Test dynamic config object generation"""

    def test_leaf_attribute_mapper(self) -> None:
        leaf = Leaf("test", "int", 42)
        result = leaf_attribute_mapper(leaf)
        assert result == 42

    def test_attribute_generation_function_mapper_leaf(self) -> None:
        leaf = Leaf("test_value", "int", 42)
        name, value = attribute_generation_function_mapper(False, leaf)
        assert name == "test_value"
        assert value == 42

    def test_tree_to_config_obj_simple(self) -> None:
        leaf1 = Leaf("value1", "int", 42)
        leaf2 = Leaf("value2", "str", "hello")
        tree = Tree("Config", (leaf1, leaf2))
        result = tree_to_config_obj(True, tree)
        assert hasattr(result, "value1")
        assert hasattr(result, "value2")
        assert result.value1 == 42
        assert result.value2 == "hello"

    def test_tree_to_config_obj_frozen(self) -> None:
        leaf = Leaf("value", "int", 42)
        tree = Tree("Config", (leaf,))
        result = tree_to_config_obj(True, tree)
        # Try to modify - should raise an error for frozen dataclass
        with pytest.raises(Exception):
            result.value = 100  # type: ignore[misc]

    def test_tree_to_config_obj_nested(self) -> None:
        inner_leaf = Leaf("inner_val", "int", 42)
        inner_struct = Structure("inner", "dict", (inner_leaf,))
        tree = Tree("Config", (inner_struct,))
        result = tree_to_config_obj(True, tree)
        assert hasattr(result, "inner")
        assert hasattr(result.inner, "inner_val")
        assert result.inner.inner_val == 42


class TestComplexScenarios:
    """Test complex real-world scenarios"""

    def test_full_workflow_simple_config(self) -> None:
        """Test complete workflow from dict to config object"""
        config_dict = {
            "name": "test",
            "version": "1.0",
            "port": 8080,
        }
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.name == "test"
        assert config.version == "1.0"
        assert config.port == 8080

    def test_full_workflow_nested_config(self) -> None:
        """Test complete workflow with nested structures"""
        config_dict = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "admin", "password": "secret"},
            },
            "app": {"name": "myapp", "debug": True},
        }
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.database.credentials.username == "admin"
        assert config.app.name == "myapp"
        assert config.app.debug is True

    def test_full_workflow_with_lists(self) -> None:
        """Test complete workflow with lists"""
        config_dict = {
            "servers": ["server1", "server2", "server3"],
            "ports": [8080, 8081, 8082],
        }
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert len(config.servers) == 3
        assert config.servers[0] == "server1"
        assert len(config.ports) == 3
        assert config.ports[1] == 8081

    def test_full_workflow_with_dates(self) -> None:
        """Test complete workflow with date objects"""
        test_date = date(2024, 1, 1)
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        config_dict = {
            "start_date": test_date,
            "created_at": test_datetime,
        }
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.start_date == test_date
        assert config.created_at == test_datetime

    def test_string_translation_complete(self) -> None:
        """Test complete string translation to stub file"""
        config_dict = {"name": "test", "value": 42}
        tree = tree_parser(config_dict)
        result = tree_to_string_translator(True, tree)
        assert "from dataclasses import dataclass" in result
        assert "class Config:" in result
        assert "name: str" in result
        assert "value: int" in result
        assert "def load_config" in result

    def test_non_dict_structure_mapper_tuple(self) -> None:
        """Test mapping of non-dict structures like tuples"""
        child1 = Leaf("item", "int", 1)
        child2 = Leaf("item", "int", 2)
        structure = Structure("items", "tuple", (child1, child2))
        result = non_dict_structure_mapper(True, structure)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == 1
        assert result[1] == 2

    def test_structure_to_str_generator_complete(self) -> None:
        """Test complete structure to string generation"""
        leaf1 = Leaf("name", "str", "test")
        leaf2 = Leaf("count", "int", 42)
        structure = Structure("TestStruct", "dict", (leaf1, leaf2))
        result = structure_to_str_generator(True, structure)
        assert "@dataclass(frozen=True)" in result
        assert "class TestStruct:" in result
        assert "name: str" in result
        assert "count: int" in result

    def test_tree_to_str_generator_complete(self) -> None:
        """Test complete tree to string generation"""
        inner_leaf = Leaf("value", "int", 42)
        inner_struct = Structure("Inner", "dict", (inner_leaf,))
        outer_leaf = Leaf("name", "str", "test")
        tree = Tree("Config", (outer_leaf, inner_struct))
        result = tree_to_str_generator(True, tree)
        assert "class Config:" in result
        assert "class Inner:" in result


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_dict(self) -> None:
        """Test handling of empty dictionaries"""
        config_dict: dict[str, int] = {}
        tree = tree_parser(config_dict)
        assert isinstance(tree, Tree)
        assert len(tree.children) == 0

    def test_special_characters_in_names(self) -> None:
        """Test handling of special characters in config keys"""
        config_dict = {"test-name": "value", "test@key": 42}
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        # Special characters should be replaced with underscores
        assert hasattr(config, "test_name")
        assert hasattr(config, "test_key")

    def test_deeply_nested_structure(self) -> None:
        """Test deeply nested configuration structures"""
        config_dict = {
            "level1": {
                "level2": {"level3": {"level4": {"level5": {"value": "deep"}}}}
            }
        }
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.level1.level2.level3.level4.level5.value == "deep"

    def test_mixed_list_types(self) -> None:
        """Test lists containing different types"""
        config_dict = {"mixed": [1, "two", 3.0]}
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.mixed[0] == 1
        assert config.mixed[1] == "two"
        assert config.mixed[2] == 3.0

    def test_none_values(self) -> None:
        """Test handling of None values"""
        config_dict = {"value": None}
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.value is None

    def test_boolean_values(self) -> None:
        """Test handling of boolean values"""
        config_dict = {"enabled": True, "disabled": False}
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.enabled is True
        assert config.disabled is False

    def test_float_values(self) -> None:
        """Test handling of float values"""
        config_dict = {"pi": 3.14159, "e": 2.71828}
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.pi == 3.14159
        assert config.e == 2.71828

    def test_path_values(self) -> None:
        """Test handling of Path objects"""
        test_path = Path("/tmp/test.txt")
        config_dict = {"file_path": test_path}
        tree = tree_parser(config_dict)
        config = tree_to_config_obj(True, tree)
        assert config.file_path == test_path
