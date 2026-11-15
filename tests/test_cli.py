"""
Tests for the command line interface (heracless.cli_tool), run end to end.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from heracless.cli_tool import main, parse_args

CONFIG = """
database:
  host: localhost
  port: 5432
"""


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(CONFIG)
    return path


class TestParseArgs:
    def test_basic(self) -> None:
        args = parse_args(["config.yaml"])
        assert args.cfg_dir == "config.yaml"
        assert args.parse is None
        assert args.dry is False

    @pytest.mark.parametrize("flag", ["--parse", "-p"])
    def test_parse(self, flag: str) -> None:
        assert parse_args(["config.yaml", flag, "out.pyi"]).parse == "out.pyi"

    @pytest.mark.parametrize("flag", ["--dry", "-d"])
    def test_dry(self, flag: str) -> None:
        assert parse_args(["config.yaml", flag]).dry is True

    def test_parse_and_dry_are_exclusive(self) -> None:
        with pytest.raises(SystemExit):
            parse_args(["config.yaml", "--dry", "--parse", "out.pyi"])

    def test_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            parse_args(["--version"])
        assert exc.value.code == 0
        assert capsys.readouterr().out.startswith("heracless ")


class TestMain:
    def test_prints_stub_by_default(self, config_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([str(config_file)]) == 0
        out = capsys.readouterr().out
        assert "class Database:\n    host: str\n    port: int\n" in out

    def test_dry_run(self, config_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([str(config_file), "--dry"]) == 0
        out = capsys.readouterr().out
        assert out.startswith("Loaded config: Config(database=Database(host='localhost', port=5432))")
        assert list(config_file.parent.iterdir()) == [config_file]  # nothing written

    @pytest.mark.parametrize("name", ["types.pyi", "types.py"])
    def test_parse_writes_pyi(self, config_file: Path, name: str, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([str(config_file), "--parse", str(config_file.parent / name)]) == 0
        stub = config_file.parent / "types.pyi"
        assert "class Database:" in stub.read_text()
        assert str(stub) in capsys.readouterr().out

    def test_yml_suffix_is_accepted(self, tmp_path: Path) -> None:
        path = tmp_path / "config.yml"
        path.write_text(CONFIG)
        assert main([str(path), "--dry"]) == 0

    @pytest.mark.parametrize(
        ("args", "message"),
        [
            (["missing.yaml"], "does not exist"),
            (["config.txt"], "is not a YAML file"),
        ],
    )
    def test_invalid_config_path(
        self, tmp_path: Path, args: list[str], message: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "config.txt").write_text(CONFIG)
        assert main([str(tmp_path / a) for a in args]) == 1
        captured = capsys.readouterr()
        assert message in captured.err
        assert captured.out == ""

    def test_invalid_stub_suffix(self, config_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([str(config_file), "--parse", "out.txt"]) == 1
        assert "must be a Python file" in capsys.readouterr().err

    def test_invalid_yaml(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        path = tmp_path / "config.yaml"
        path.write_text("a: [1\n")
        assert main([str(path)]) == 1
        assert "Syntax Error" in capsys.readouterr().err

    def test_empty_config(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        path = tmp_path / "config.yaml"
        path.write_text("")
        assert main([str(path), "--parse", str(tmp_path / "types.pyi")]) == 1
        assert "is empty" in capsys.readouterr().err
        assert not (tmp_path / "types.pyi").exists()

    def test_missing_stub_directory(self, config_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([str(config_file), "--parse", str(config_file.parent / "nope" / "types.pyi")]) == 1
        assert "nope" in capsys.readouterr().err


def test_python_dash_m(config_file: Path) -> None:
    """`python -m heracless` is the documented way to run the CLI."""
    result = subprocess.run(
        [sys.executable, "-m", "heracless", str(config_file)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert "class Config:" in result.stdout

    result = subprocess.run(
        [sys.executable, "-m", "heracless", "missing.yaml"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 1
