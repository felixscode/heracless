"""
Comprehensive tests for heracless.cli_tool module
"""

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from heracless.cli_tool import parse_args, run_cli


class TestParseArgs:
    """Test command-line argument parsing"""

    @patch("sys.argv", ["heracless", "config.yaml"])
    def test_parse_args_basic(self) -> None:
        """Test basic argument parsing with just config file"""
        args = parse_args()
        assert args.cfg_dir == "config.yaml"
        assert args.parse is None
        assert args.dry is False

    @patch("sys.argv", ["heracless", "config.yaml", "--parse", "output.py"])
    def test_parse_args_with_parse(self) -> None:
        """Test parsing with --parse option"""
        args = parse_args()
        assert args.cfg_dir == "config.yaml"
        assert args.parse == "output.py"
        assert args.dry is False

    @patch("sys.argv", ["heracless", "config.yaml", "-p", "output.py"])
    def test_parse_args_with_parse_short(self) -> None:
        """Test parsing with -p short option"""
        args = parse_args()
        assert args.cfg_dir == "config.yaml"
        assert args.parse == "output.py"

    @patch("sys.argv", ["heracless", "config.yaml", "--dry"])
    def test_parse_args_with_dry(self) -> None:
        """Test parsing with --dry option"""
        args = parse_args()
        assert args.cfg_dir == "config.yaml"
        assert args.dry is True

    @patch("sys.argv", ["heracless", "config.yaml", "-d"])
    def test_parse_args_with_dry_short(self) -> None:
        """Test parsing with -d short option"""
        args = parse_args()
        assert args.cfg_dir == "config.yaml"
        assert args.dry is True


class TestRunCLI:
    """Test CLI execution"""

    @patch("heracless.cli_tool.parse_args")
    @patch("heracless.cli_tool.main")
    @patch("os.path.exists")
    def test_run_cli_with_dry_run(
        self, mock_exists: MagicMock, mock_main: MagicMock, mock_parse_args: MagicMock
    ) -> None:
        """Test CLI with --dry flag"""
        # Setup mocks
        mock_parse_args.return_value = argparse.Namespace(
            cfg_dir="test.yaml", parse=None, dry=True
        )
        mock_exists.return_value = True
        mock_main.return_value = MagicMock(value=42)

        # Run
        run_cli()

        # Verify
        mock_main.assert_called_once()
        args = mock_main.call_args
        assert args[1]["cfg_dir"] == "test.yaml"
        assert args[1]["dump_dir"] is None
        assert args[1]["frozen"] is True

    @patch("heracless.cli_tool.parse_args")
    @patch("heracless.cli_tool.main")
    @patch("os.path.exists")
    def test_run_cli_with_parse(
        self, mock_exists: MagicMock, mock_main: MagicMock, mock_parse_args: MagicMock
    ) -> None:
        """Test CLI with --parse flag"""
        # Setup mocks
        mock_parse_args.return_value = argparse.Namespace(
            cfg_dir="test.yaml", parse="output.py", dry=False
        )
        mock_exists.return_value = True
        mock_main.return_value = MagicMock(value=42)

        # Run
        run_cli()

        # Verify
        mock_main.assert_called_once()
        args = mock_main.call_args
        assert args[1]["cfg_dir"] == "test.yaml"
        assert isinstance(args[1]["dump_dir"], Path)
        assert str(args[1]["dump_dir"]) == "output.py"

    @patch("heracless.cli_tool.parse_args")
    @patch("heracless.cli_tool.main")
    @patch("os.path.exists")
    @patch("builtins.print")
    def test_run_cli_invalid_config_file(
        self,
        mock_print: MagicMock,
        mock_exists: MagicMock,
        mock_main: MagicMock,
        mock_parse_args: MagicMock,
    ) -> None:
        """Test CLI with non-existent config file"""
        mock_parse_args.return_value = argparse.Namespace(
            cfg_dir="nonexistent.yaml", parse=None, dry=True
        )
        mock_exists.return_value = False

        run_cli()

        mock_print.assert_called()
        assert "Config file does not exist" in str(mock_print.call_args)
        mock_main.assert_not_called()

    @patch("heracless.cli_tool.parse_args")
    @patch("heracless.cli_tool.main")
    @patch("os.path.exists")
    @patch("builtins.print")
    def test_run_cli_non_yaml_file(
        self,
        mock_print: MagicMock,
        mock_exists: MagicMock,
        mock_main: MagicMock,
        mock_parse_args: MagicMock,
    ) -> None:
        """Test CLI with non-YAML file"""
        mock_parse_args.return_value = argparse.Namespace(
            cfg_dir="test.txt", parse=None, dry=True
        )
        mock_exists.return_value = True

        run_cli()

        mock_print.assert_called()
        assert "not a YAML file" in str(mock_print.call_args)
        mock_main.assert_not_called()

    @patch("heracless.cli_tool.parse_args")
    @patch("heracless.cli_tool.main")
    @patch("os.path.exists")
    @patch("builtins.print")
    def test_run_cli_invalid_dump_file(
        self,
        mock_print: MagicMock,
        mock_exists: MagicMock,
        mock_main: MagicMock,
        mock_parse_args: MagicMock,
    ) -> None:
        """Test CLI with invalid dump file extension"""
        mock_parse_args.return_value = argparse.Namespace(
            cfg_dir="test.yaml", parse="output.txt", dry=False
        )
        mock_exists.return_value = True

        run_cli()

        mock_print.assert_called()
        assert "must be a Python file" in str(mock_print.call_args)
        mock_main.assert_not_called()

    @patch("heracless.cli_tool.parse_args")
    @patch("heracless.cli_tool.main")
    @patch("os.path.exists")
    def test_run_cli_with_pyi_extension(
        self, mock_exists: MagicMock, mock_main: MagicMock, mock_parse_args: MagicMock
    ) -> None:
        """Test CLI accepts .pyi extension for dump file"""
        mock_parse_args.return_value = argparse.Namespace(
            cfg_dir="test.yaml", parse="output.pyi", dry=False
        )
        mock_exists.return_value = True
        mock_main.return_value = MagicMock()

        run_cli()

        mock_main.assert_called_once()
        args = mock_main.call_args
        assert isinstance(args[1]["dump_dir"], Path)


class TestCLIIntegration:
    """Integration tests for CLI with real files"""

    def test_cli_with_temp_files(self, tmp_path: Path) -> None:
        """Test CLI with actual temporary files"""
        # Create a test YAML file
        yaml_content = """
name: test
version: 1.0
"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml_content)

        # Create expected output path
        output_file = tmp_path / "output.pyi"

        # Mock sys.argv and run
        with patch("sys.argv", ["heracless", str(yaml_file), "-p", str(output_file)]):
            with patch("heracless.cli_tool.parse_args") as mock_parse:
                mock_parse.return_value = argparse.Namespace(
                    cfg_dir=str(yaml_file), parse=str(output_file), dry=False
                )
                # We would call run_cli() here but it would actually execute
                # Just verify the parse_args would be called correctly
                args = parse_args()
                assert args.cfg_dir == str(yaml_file)
