"""
Tests for loading configs: the object model, helpers, stubs and error handling.
"""

import dataclasses
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

import heracless
from heracless import (
    ConfigError,
    DirectoryError,
    YamlSyntaxError,
    as_dict,
    from_dict,
    generate_stub,
    load_config,
    mutate_config,
)
from heracless.fight import fight, load_as_dict


def write(tmp_path: Path, content: str, name: str = "config.yaml") -> Path:
    path = tmp_path / name
    path.write_text(content)
    return path


def run_mypy(*files: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "--no-incremental", *map(str, files)],
        capture_output=True,
        text=True,
        check=False,
        cwd=files[0].parent,
    )


class TestInvoiceExample:
    def test_values(self, config_path: Path) -> None:
        config = load_config(config_path)
        assert config.invoice == 34843
        assert config.date == date(2001, 1, 23)
        assert config.bill_to.given == "Chris"
        assert config.bill_to.address.city == "Royal Oak"
        assert config.ship_to.address.postal == 48046
        assert config.product[0].sku == "BL394D"
        assert config.product[1].price == 2392.0
        assert config.tax == 251.42
        assert config.comments == "Late afternoon is best. Backup contact is Nancy Billsmer @ 338-4338."

    def test_load_as_dict(self, config_path: Path, cfg_dict: dict[str, Any]) -> None:
        assert load_as_dict(config_path) == cfg_dict

    def test_identical_nested_mappings_share_a_class(self, config_path: Path) -> None:
        config = load_config(config_path)
        assert type(config.bill_to.address) is type(config.ship_to.address)
        assert type(config.product[0]) is type(config.product[1])

    def test_fight_alias(self, config_path: Path) -> None:
        # Every load creates its own classes, so compare representations.
        assert repr(fight(cfg_dir=config_path, dump_dir=None, frozen=True)) == repr(load_config(config_path))

    def test_dict_round_trip(self, config_path: Path) -> None:
        config = load_config(config_path)
        assert repr(from_dict(as_dict(config))) == repr(config)
        assert as_dict(config)["product"][0]["sku"] == "BL394D"

    def test_mutate(self, config_path: Path) -> None:
        config = load_config(config_path)
        changed = mutate_config(config, "bill_to.address.city", "New City")
        assert changed.bill_to.address.city == "New City"
        assert config.bill_to.address.city == "Royal Oak"
        assert mutate_config(config, "invoice", 0).invoice == 0

    def test_mutate_unknown_field(self, config_path: Path) -> None:
        config = load_config(config_path)
        with pytest.raises(AttributeError, match="no field 'nope'"):
            mutate_config(config, "bill_to.nope", 1)


class TestFrozen:
    def test_frozen_by_default(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "a: {b: 1}\n"))
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.a.b = 2

    def test_frozen_false_is_honoured(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "a: {b: 1}\n"), frozen=False)
        config.a.b = 2
        assert config.a.b == 2

    def test_from_dict_frozen_false(self) -> None:
        config = from_dict({"a": {"b": 1}}, frozen=False)
        config.a.b = 2
        assert config.a.b == 2


class TestShapes:
    def test_empty_collections(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "items: []\nsection: {}\n"))
        assert config.items == ()
        assert dataclasses.fields(config.section) == ()

    def test_lists_become_tuples(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "a: [[1, 2], [3]]\n"))
        assert config.a == ((1, 2), (3,))

    def test_list_items_with_different_keys(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "users:\n  - {name: a, age: 1}\n  - {name: b, email: e}\n"))
        assert type(config.users[0]) is type(config.users[1])
        assert config.users[0].email is None
        assert config.users[1].age is None

    def test_conflicting_class_names(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "server: {host: h}\nother:\n  server: {name: n}\n"))
        assert type(config.server).__name__ == "Server"
        assert type(config.other.server).__name__ == "OtherServer"
        assert config.other.server.name == "n"

    def test_key_names(self, tmp_path: Path) -> None:
        config = load_config(
            write(
                tmp_path,
                "my-key: 1\nmy_key: 2\nHTTPServer: 3\nclass: 4\n1st: 5\ncamelCase: 6\nnone: {a: 1}\n",
            )
        )
        assert [f.name for f in dataclasses.fields(config)] == [
            "my_key",
            "my_key_1",
            "http_server",
            "class_",
            "_1st",
            "camel_case",
            "none",
        ]
        assert type(config.none).__name__ == "None_"

    def test_timestamps(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "a: 2001-12-14t21:59:43.10-05:00\nb: 2001-12-14 21:59:43\n"))
        assert config.a == datetime(2001, 12, 14, 21, 59, 43, 100000, tzinfo=timezone(timedelta(hours=-5)))
        assert config.b.tzinfo is None

    def test_big_integers(self, tmp_path: Path) -> None:
        config = load_config(write(tmp_path, "a: 123456789012345678901234567890\nb: 0x1FFFFFFFFFFFFFFFF\n"))
        assert config.a == 123456789012345678901234567890
        assert config.b == 0x1FFFFFFFFFFFFFFFF

    def test_from_dict_keeps_arbitrary_objects(self) -> None:
        marker = object()
        config = from_dict({"path": Path("/x"), "obj": marker, "when": date(2020, 1, 1), "n": [1, 2]})
        assert config.path == Path("/x")
        assert config.obj is marker
        assert config.n == (1, 2)

    def test_from_dict_rejects_non_mappings(self) -> None:
        with pytest.raises(TypeError, match="expects a dict"):
            from_dict([1, 2])  # type: ignore[arg-type]

    def test_from_dict_rejects_cycles(self) -> None:
        cyclic: dict[str, Any] = {}
        cyclic["self"] = cyclic
        with pytest.raises(ValueError, match="nested deeper"):
            from_dict(cyclic)


class TestErrors:
    def test_missing_file_is_not_created(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.yaml"
        with pytest.raises(DirectoryError):
            load_config(missing)
        assert not missing.exists()

    def test_missing_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))

    def test_directory_instead_of_file(self, tmp_path: Path) -> None:
        with pytest.raises(OSError):
            load_config(tmp_path)

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        with pytest.raises(YamlSyntaxError, match=r"line \d+, column \d+"):
            load_config(write(tmp_path, "a: [1\n"))

    def test_multiple_documents(self, tmp_path: Path) -> None:
        with pytest.raises(YamlSyntaxError, match="single document"):
            load_config(write(tmp_path, "a: 1\n---\nb: 2\n"))

    def test_unsupported_tag(self, tmp_path: Path) -> None:
        with pytest.raises(YamlSyntaxError, match="unsupported tag"):
            load_config(write(tmp_path, "a: !!python/object:os.system x\n"))

    @pytest.mark.parametrize("content", ["- a\n- b\n", "just a string\n", "42\n"])
    def test_root_must_be_a_mapping(self, tmp_path: Path, content: str) -> None:
        with pytest.raises(ConfigError, match="must be a mapping"):
            load_config(write(tmp_path, content))

    @pytest.mark.parametrize("content", ["", "# just a comment\n", "~\n"])
    def test_empty_config_is_none(self, tmp_path: Path, content: str) -> None:
        stub = tmp_path / "types.pyi"
        assert load_config(write(tmp_path, content), stub) is None
        assert not stub.exists()

    def test_stub_directory_must_exist(self, tmp_path: Path) -> None:
        with pytest.raises(DirectoryError):
            load_config(write(tmp_path, "a: 1\n"), tmp_path / "nope" / "types.pyi")

    def test_exception_hierarchy(self) -> None:
        assert issubclass(YamlSyntaxError, heracless.HeraclessError)
        assert issubclass(YamlSyntaxError, ValueError)
        assert issubclass(ConfigError, ValueError)
        assert issubclass(DirectoryError, FileNotFoundError)


class TestStubs:
    def test_stub_suffix_is_pyi(self, tmp_path: Path) -> None:
        load_config(write(tmp_path, "a: 1\n"), tmp_path / "load_config.py")
        assert (tmp_path / "load_config.pyi").exists()
        assert not (tmp_path / "load_config.py").exists()

    def test_stub_is_deterministic_and_not_rewritten(self, tmp_path: Path, config_path: Path) -> None:
        stub = tmp_path / "types.pyi"
        load_config(config_path, stub)
        first, mtime = stub.read_text(), stub.stat().st_mtime_ns
        load_config(config_path, stub)
        assert stub.read_text() == first
        assert stub.stat().st_mtime_ns == mtime
        assert generate_stub(config_path) == first

    def test_stub_matches_runtime_field_names(self, tmp_path: Path) -> None:
        config_file = write(tmp_path, "my-key: 1\nmy_key: 2\nclass: {x: 1}\n")
        stub = tmp_path / "types.pyi"
        config = load_config(config_file, stub)
        for field in dataclasses.fields(config):
            assert f"    {field.name}: " in stub.read_text()

    def test_client_code_type_checks(self, tmp_path: Path) -> None:
        """The README workflow: a load_config module, its generated stub, and client code."""
        write(
            tmp_path,
            """
ports: [80, 443]
db: {host: localhost, port: 5432}
users:
  - {name: a, age: 1}
  - {name: b}
started: 2020-01-01
datetime: not the module
int: 3
""",
        )
        (tmp_path / "load_config.py").write_text(
            "from pathlib import Path\n"
            "from typing import Any\n"
            "from heracless import load_config as _load_config\n\n"
            "Config = Any  # the generated stub declares the real class\n\n"
            "def load_config(config_path: Path | str | None = None, frozen: bool = True, "
            "stub_dump: bool = True) -> Any:\n"
            "    path = config_path or Path(__file__).parent / 'config.yaml'\n"
            "    return _load_config(path, Path(__file__) if stub_dump else None, frozen=frozen)\n"
        )
        main = tmp_path / "main.py"
        main.write_text(
            "import datetime\n"
            "from load_config import Config, load_config\n\n"
            "config: Config = load_config()\n"
            "second_port: int = config.ports[1]\n"
            "host: str = config.db.host\n"
            "age: int | None = config.users[1].age\n"
            "started: datetime.date = config.started\n"
            "count: int = config.int\n"
        )
        result = subprocess.run([sys.executable, str(main)], capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr
        assert (tmp_path / "load_config.pyi").exists()

        result = run_mypy(tmp_path / "load_config.pyi", main)
        assert result.returncode == 0, result.stdout

        main.write_text("from load_config import load_config\n\nload_config().db.hots\n")
        result = run_mypy(tmp_path / "load_config.pyi", main)
        assert result.returncode == 1
        assert 'has no attribute "hots"' in result.stdout


def test_version() -> None:
    assert heracless.__version__ != "unknown"
