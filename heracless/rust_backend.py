"""
Rust backend wrapper for Heracless

This module provides a Python interface to the Rust-powered core functions.
Falls back to pure Python implementation if Rust extension is not available.
"""

import json
from pathlib import Path
from typing import Optional, Any, cast
import warnings

try:
    from heracless_core import generate_python_stubs, parse_yaml_to_json  # type: ignore[import-not-found]
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    warnings.warn(
        "Rust backend not available, falling back to pure Python implementation. "
        "For better performance, build the Rust extension with: maturin develop"
    )


def generate_stubs_rust(config_path: Path, frozen: bool) -> str:
    """
    Generate Python type stubs using Rust backend

    Args:
        config_path: Path to YAML config file
        frozen: Whether dataclasses should be frozen

    Returns:
        Generated Python code as string
    """
    if not RUST_AVAILABLE:
        raise RuntimeError("Rust backend not available")

    result: str = generate_python_stubs(str(config_path), frozen)
    return result


def parse_yaml_rust(config_path: Path) -> dict[Any, Any]:
    """
    Parse YAML file using Rust backend

    Args:
        config_path: Path to YAML config file

    Returns:
        Parsed YAML as Python dictionary
    """
    if not RUST_AVAILABLE:
        raise RuntimeError("Rust backend not available")

    json_str: str = parse_yaml_to_json(str(config_path))
    result: dict[Any, Any] = json.loads(json_str)
    return result


def is_rust_available() -> bool:
    """Check if Rust backend is available"""
    return RUST_AVAILABLE
