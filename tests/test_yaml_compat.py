"""
The Rust YAML loader must resolve documents exactly like PyYAML's ``full_load``
(which heracless used before its core moved to Rust), so configs keep their types.
"""

import math
from pathlib import Path
from typing import Any

import pytest
import yaml

from heracless.fight import load_as_dict

SCALARS = [
    # null
    "~", "null", "Null", "NULL", "", "nil", "None",
    # booleans (YAML 1.1)
    "true", "True", "TRUE", "false", "yes", "Yes", "NO", "on", "Off", "y", "n", "tRUE",
    # integers
    "0", "42", "-17", "+5", "1_000_000", "017", "0o17", "0b1010", "-0b11", "0x1F", "0xff_ff", "1:30", "-1:00:01",
    "08", "007", "123456789012345678901234567890", "-9223372036854775808", "9223372036854775808",
    # floats
    "1.5", "-0.25", "1.", ".5", "1.e+3", "6.8523015e+5", "1e3", "1.0e5", "1_000.5", ".inf", "-.Inf", "+.INF",
    ".nan", ".NaN", "190:20:30.15", "1.2.3",
    # timestamps
    "2001-12-14", "2001-12-14t21:59:43.10-05:00", "2001-12-14 21:59:43.10 -5", "2001-12-14T21:59:43Z",
    "2002-12-14 2:59:43", "2001-1-1 1:00:00", "2001-1-1", "2001-12-14 21:59:43.1234567",
    # strings that look like something else
    "'42'", '"true"', "!!str 42", "1.0.0", "v1.2", "12:30:00:00:00:00:00", "localhost:8080", "0x",
    "a b c", "'  padded  '", "\"tab\\tnewline\\n\"",
    # explicit tags
    "!!int '42'", "!!float 3", "!!float '1.5'", "!!bool yes", "!!null ''", "!!str yes", "!!timestamp 2001-01-01",
]  # fmt: skip

DOCUMENTS = [
    "a: 1\nb: [1, 2, {c: d}]\n",
    "base: &base {x: 1, y: 2}\nderived:\n  <<: *base\n  y: 3\n",
    "a: &a {x: 1, y: 1}\nb: &b {y: 2, z: 2}\nc:\n  <<: [*a, *b]\n  z: 3\n",
    "a: &a {x: 1}\nb: &b {x: 2}\nc:\n  <<: *a\n  <<: *b\n",
    "list: &l [1, 2]\ncopy: *l\n",
    "block: |\n  line 1\n  line 2\nfolded: >\n  folded\n  text\n\nkeep: |+\n  x\n\n",
    "dup: 1\ndup: 2\n",
    "set: !!set {a, b}\n",
    "omap: !!omap [{a: 1}, {b: 2}]\n",
    "flow: {a: [1, {b: c}], 'd': \"e\"}\n",
    "empty_map: {}\nempty_list: []\nempty_value:\n",
    "---\na: 1\n...\n",
    "﻿bom: true\n",
    "",
    "# only a comment\n",
]


def same(a: Any, b: Any) -> bool:
    """Equality that also checks types (True != 1) and treats NaN as equal to NaN."""
    if type(a) is not type(b):
        return False
    if isinstance(a, float) and math.isnan(a):
        return math.isnan(b)
    if isinstance(a, dict):
        return list(a) == list(b) and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return bool(a == b)


def rust_load(tmp_path: Path, content: str) -> Any:
    path = tmp_path / "doc.yaml"
    path.write_text(content, encoding="utf-8")
    return load_as_dict(path)


def normalize(value: Any) -> Any:
    """PyYAML returns sets for !!set and tuples for !!omap pairs; heracless returns lists."""
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [list(v) if isinstance(v, tuple) else normalize(v) for v in value]
    return value


@pytest.mark.parametrize("scalar", SCALARS)
def test_scalars_match_pyyaml(tmp_path: Path, scalar: str) -> None:
    document = f"value: {scalar}\n"
    expected = yaml.full_load(document)
    actual = rust_load(tmp_path, document)
    assert same(actual, expected), f"{scalar!r}: heracless={actual!r} pyyaml={expected!r}"


@pytest.mark.parametrize("document", DOCUMENTS)
def test_documents_match_pyyaml(tmp_path: Path, document: str) -> None:
    expected = normalize(yaml.full_load(document.lstrip("﻿")))
    actual = rust_load(tmp_path, document)
    if "!!set" in document:
        actual = {k: sorted(v) for k, v in actual.items()}
    if "!!omap" in document:
        actual = {k: [list(item.items())[0] for item in v] for k, v in actual.items()}
        actual = {k: [list(pair) for pair in v] for k, v in actual.items()}
    assert same(actual, expected), f"heracless={actual!r} pyyaml={expected!r}"


def test_non_string_keys_are_stringified(tmp_path: Path) -> None:
    """Keys become attribute names, so they are converted with str().

    PyYAML keeps them as Python objects, so there `yes` (True) even overwrites the key `1`.
    """
    document = "1: int\nyes: bool\n~: none\n1.5: float\n2001-01-01: date\n"
    expected = {"1": "int", "True": "bool", "None": "none", "1.5": "float", "2001-01-01": "date"}
    assert rust_load(tmp_path, document) == expected


@pytest.mark.parametrize("document", ["a: 2001-02-30\n", "a: !!int x\n", "a: [1\n", "a: *missing\n"])
def test_both_reject(tmp_path: Path, document: str) -> None:
    with pytest.raises(Exception):
        yaml.full_load(document)
    with pytest.raises(Exception):
        rust_load(tmp_path, document)
