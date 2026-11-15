"""Type stubs for the Rust extension module ``heracless._core``."""

import os
from typing import Any

def load_config(path: str | os.PathLike[str], frozen: bool = True, stub_path: str | os.PathLike[str] | None = None) -> Any:
    """Load a YAML config into a dataclass instance (``None`` for an empty file), optionally writing a stub."""

def generate_stub(path: str | os.PathLike[str], frozen: bool = True) -> str | None:
    """Return the ``.pyi`` type stub for a YAML config (``None`` for an empty file)."""

def load_yaml(path: str | os.PathLike[str]) -> Any:
    """Parse a YAML file into plain dicts, lists and scalars."""

def from_dict(data: Any, frozen: bool = True) -> Any:
    """Build a config dataclass instance from a dict."""
