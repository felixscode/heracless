"""
Comprehensive tests for heracless.utils.utils and heracless.utils.exceptions modules
"""

from pathlib import Path

import pytest

from heracless.utils.exceptions import DirectoryError, NotIterable, YamlSyntaxError
from heracless.utils.utils import (
    dump_template_to_file,
    insert_path_into_load_config_template,
    path_exists,
)


class TestPathExists:
    """Test path_exists function"""

    def test_path_exists_creates_file(self, tmp_path: Path) -> None:
        """Test that path_exists creates a file if it doesn't exist"""
        test_file = tmp_path / "test.txt"
        assert not test_file.exists()

        path_exists(test_file)

        assert test_file.exists()

    def test_path_exists_with_existing_file(self, tmp_path: Path) -> None:
        """Test that path_exists works with existing file"""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        assert test_file.exists()

        # Should not raise an error
        path_exists(test_file)
        assert test_file.exists()

    def test_path_exists_raises_error_for_nonexistent_parent(self) -> None:
        """Test that path_exists raises error when parent directory doesn't exist"""
        non_existent_path = Path("/nonexistent/directory/file.txt")

        with pytest.raises(DirectoryError):
            path_exists(non_existent_path)

    def test_path_exists_with_nested_directory(self, tmp_path: Path) -> None:
        """Test path_exists with nested directory structure"""
        nested_dir = tmp_path / "level1" / "level2"
        nested_dir.mkdir(parents=True)
        test_file = nested_dir / "test.txt"

        path_exists(test_file)

        assert test_file.exists()

    def test_path_exists_idempotent(self, tmp_path: Path) -> None:
        """Test that calling path_exists multiple times is safe"""
        test_file = tmp_path / "test.txt"

        path_exists(test_file)
        path_exists(test_file)
        path_exists(test_file)

        assert test_file.exists()


class TestInsertPathIntoLoadConfigTemplate:
    """Test insert_path_into_load_config_template function"""

    def test_insert_path_basic(self) -> None:
        """Test basic path insertion into template"""
        test_path = Path("/path/to/config.yaml")
        result = insert_path_into_load_config_template(test_path)

        assert isinstance(result, list)
        assert len(result) > 0
        # Check that the path was inserted
        assert any(str(test_path) in line for line in result)

    def test_insert_path_replaces_config_yaml_path_line(self) -> None:
        """Test that CONFIG_YAML_PATH line is replaced"""
        test_path = Path("/path/to/config.yaml")
        result = insert_path_into_load_config_template(test_path)

        # Find the line that should contain our path
        config_path_lines = [line for line in result if "CONFIG_YAML_PATH" in line]
        assert len(config_path_lines) > 0
        assert str(test_path) in config_path_lines[0]

    def test_insert_path_preserves_other_lines(self) -> None:
        """Test that other lines in template are preserved"""
        test_path = Path("/path/to/config.yaml")
        result = insert_path_into_load_config_template(test_path)

        # Should contain import statements
        has_imports = any("import" in line or "from" in line for line in result)
        assert has_imports

    def test_insert_path_with_different_paths(self) -> None:
        """Test insertion with various path formats"""
        paths = [
            Path("/absolute/path/config.yaml"),
            Path("relative/path/config.yaml"),
            Path("./config.yaml"),
            Path("../parent/config.yaml"),
        ]

        for test_path in paths:
            result = insert_path_into_load_config_template(test_path)
            assert any(str(test_path) in line for line in result)


class TestDumpTemplateToFile:
    """Test dump_template_to_file function"""

    def test_dump_template_creates_file(self, tmp_path: Path) -> None:
        """Test that dump_template_to_file creates a file"""
        config_path = Path("/path/to/config.yaml")
        output_file = tmp_path / "output.py"

        dump_template_to_file(config_path, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert len(content) > 0
        assert str(config_path) in content

    def test_dump_template_does_not_overwrite_by_default(self, tmp_path: Path) -> None:
        """Test that dump_template_to_file doesn't overwrite existing file by default"""
        config_path = Path("/path/to/config.yaml")
        output_file = tmp_path / "output.py"

        # Create file with initial content
        initial_content = "# Initial content"
        output_file.write_text(initial_content)

        # Try to dump template (should not overwrite)
        dump_template_to_file(config_path, output_file, force=False)

        # Content should remain unchanged
        assert output_file.read_text() == initial_content

    def test_dump_template_overwrites_with_force(self, tmp_path: Path) -> None:
        """Test that dump_template_to_file overwrites when force=True"""
        config_path = Path("/path/to/config.yaml")
        output_file = tmp_path / "output.py"

        # Create file with initial content
        initial_content = "# Initial content"
        output_file.write_text(initial_content)

        # Dump template with force=True
        dump_template_to_file(config_path, output_file, force=True)

        # Content should be changed
        new_content = output_file.read_text()
        assert new_content != initial_content
        assert str(config_path) in new_content

    def test_dump_template_with_nested_directory(self, tmp_path: Path) -> None:
        """Test dump_template_to_file with nested directory"""
        config_path = Path("/path/to/config.yaml")
        nested_dir = tmp_path / "level1" / "level2"
        nested_dir.mkdir(parents=True)
        output_file = nested_dir / "output.py"

        dump_template_to_file(config_path, output_file)

        assert output_file.exists()
        assert str(config_path) in output_file.read_text()

    def test_dump_template_content_structure(self, tmp_path: Path) -> None:
        """Test that dumped template has expected structure"""
        config_path = Path("/path/to/config.yaml")
        output_file = tmp_path / "output.py"

        dump_template_to_file(config_path, output_file)

        content = output_file.read_text()
        # Should have imports
        assert "import" in content or "from" in content
        # Should have load_config function
        assert "load_config" in content
        # Should have the config path
        assert str(config_path) in content


class TestDirectoryError:
    """Test DirectoryError exception"""

    def test_directory_error_creation(self) -> None:
        """Test creating DirectoryError with Path"""
        path = Path("/nonexistent/path")
        error = DirectoryError(path)
        assert error.given_dir == path

    def test_directory_error_creation_with_string(self) -> None:
        """Test creating DirectoryError with string"""
        path_str = "/nonexistent/path"
        error = DirectoryError(path_str)
        assert error.given_dir == path_str

    def test_directory_error_str_representation(self) -> None:
        """Test string representation of DirectoryError"""
        path = Path("/nonexistent/path")
        error = DirectoryError(path)
        error_str = str(error)
        assert str(path) in error_str
        assert "not existing" in error_str.lower()

    def test_directory_error_can_be_raised(self) -> None:
        """Test that DirectoryError can be raised and caught"""
        path = Path("/nonexistent/path")

        with pytest.raises(DirectoryError) as exc_info:
            raise DirectoryError(path)

        assert exc_info.value.given_dir == path

    def test_directory_error_inheritance(self) -> None:
        """Test that DirectoryError inherits from Exception"""
        path = Path("/nonexistent/path")
        error = DirectoryError(path)
        assert isinstance(error, Exception)


class TestNotIterable:
    """Test NotIterable exception"""

    def test_not_iterable_creation(self) -> None:
        """Test creating NotIterable with value"""
        value = 42
        error = NotIterable(value)
        assert error.value == value

    def test_not_iterable_str_representation(self) -> None:
        """Test string representation of NotIterable"""
        value = 42
        error = NotIterable(value)
        error_str = str(error)
        assert "int" in error_str
        assert "not iteratable" in error_str.lower()

    def test_not_iterable_with_different_types(self) -> None:
        """Test NotIterable with various non-iterable types"""
        values = [42, 3.14, True, None]

        for value in values:
            error = NotIterable(value)
            assert error.value == value
            error_str = str(error)
            assert type(value).__name__ in error_str

    def test_not_iterable_can_be_raised(self) -> None:
        """Test that NotIterable can be raised and caught"""
        value = 42

        with pytest.raises(NotIterable) as exc_info:
            raise NotIterable(value)

        assert exc_info.value.value == value

    def test_not_iterable_inheritance(self) -> None:
        """Test that NotIterable inherits from Exception"""
        value = 42
        error = NotIterable(value)
        assert isinstance(error, Exception)


class TestYamlSyntaxError:
    """Test YamlSyntaxError exception"""

    def test_yaml_syntax_error_creation(self) -> None:
        """Test creating YamlSyntaxError"""
        exception_msg = "Invalid YAML syntax"
        error = YamlSyntaxError(exception_msg)
        assert error.value == exception_msg

    def test_yaml_syntax_error_str_representation(self) -> None:
        """Test string representation of YamlSyntaxError"""
        exception_msg = "Invalid YAML: unexpected character"
        error = YamlSyntaxError(exception_msg)
        error_str = str(error)
        assert "Syntax Error" in error_str
        assert exception_msg in error_str

    def test_yaml_syntax_error_with_complex_message(self) -> None:
        """Test YamlSyntaxError with complex error message"""
        exception_msg = "YAML error at line 42: unexpected token"
        error = YamlSyntaxError(exception_msg)
        error_str = str(error)
        assert exception_msg in error_str
        assert "YAML" in error_str

    def test_yaml_syntax_error_can_be_raised(self) -> None:
        """Test that YamlSyntaxError can be raised and caught"""
        exception_msg = "Test YAML error"

        with pytest.raises(YamlSyntaxError) as exc_info:
            raise YamlSyntaxError(exception_msg)

        assert exc_info.value.value == exception_msg

    def test_yaml_syntax_error_inheritance(self) -> None:
        """Test that YamlSyntaxError inherits from Exception"""
        exception_msg = "Test error"
        error = YamlSyntaxError(exception_msg)
        assert isinstance(error, Exception)


class TestExceptionsIntegration:
    """Integration tests for exception handling"""

    def test_directory_error_in_path_exists(self) -> None:
        """Test that path_exists raises DirectoryError appropriately"""
        non_existent = Path("/absolutely/nonexistent/path/file.txt")

        with pytest.raises(DirectoryError) as exc_info:
            path_exists(non_existent)

        error = exc_info.value
        assert isinstance(error.given_dir, Path) or isinstance(error.given_dir, str)

    def test_exception_chaining(self) -> None:
        """Test that exceptions can be chained"""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            with pytest.raises(DirectoryError):
                raise DirectoryError(Path("/test")) from e


class TestUtilsEdgeCases:
    """Test edge cases in utils module"""

    def test_path_exists_with_symbolic_link(self, tmp_path: Path) -> None:
        """Test path_exists behavior with symbolic links"""
        # This test may be skipped on Windows where symlinks require admin privileges
        try:
            real_file = tmp_path / "real.txt"
            real_file.touch()
            symlink = tmp_path / "link.txt"
            symlink.symlink_to(real_file)

            # Should work with symlink
            path_exists(symlink)
            assert symlink.exists()
        except (OSError, NotImplementedError):
            pytest.skip("Symbolic links not supported on this platform")

    def test_dump_template_with_unicode_path(self, tmp_path: Path) -> None:
        """Test dump_template_to_file with unicode characters in path"""
        config_path = Path("/path/to/配置文件.yaml")
        output_file = tmp_path / "output.py"

        dump_template_to_file(config_path, output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "配置文件" in content

    def test_path_exists_with_empty_filename(self, tmp_path: Path) -> None:
        """Test path_exists with just directory path"""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        # Calling path_exists on a directory that exists shouldn't create anything new
        path_exists(test_dir)
        assert test_dir.is_dir()
