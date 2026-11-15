"""Exceptions raised by heracless.

They are raised directly by the Rust core (``heracless._core``), so keep the class
names and constructor signatures stable.
"""

import errno
from pathlib import Path
from typing import Any


class HeraclessError(Exception):
    """Base class for all heracless errors."""


class DirectoryError(HeraclessError, FileNotFoundError):
    """A config file, or the directory a stub should be written to, does not exist.

    Subclasses :class:`FileNotFoundError`, so ``except FileNotFoundError`` works too.
    """

    def __init__(self, given_dir: Path | str, *args: Any) -> None:
        super().__init__(errno.ENOENT, "No such file or directory", str(given_dir))
        self.given_dir = given_dir

    def __str__(self) -> str:
        return f"The given Directory or Path: {self.given_dir} is not existing"


class YamlSyntaxError(HeraclessError, ValueError):
    """The config file is not valid YAML (or uses unsupported YAML features such as custom tags)."""

    def __init__(self, exception: Any, *args: Any) -> None:
        super().__init__(exception, *args)
        self.value = exception

    def __str__(self) -> str:
        return f"Syntax Error in your YAML File:\n {self.value}"


class ConfigError(HeraclessError, ValueError):
    """The YAML is valid but can't be turned into a config (e.g. its top level is a list)."""


class NotIterable(HeraclessError, TypeError):
    """Kept for backwards compatibility; heracless no longer raises it."""

    def __init__(self, value: Any, *args: Any) -> None:
        super().__init__(value, *args)
        self.value = value

    def __str__(self) -> str:
        return f"The given value of type: {type(self.value)} is not iteratable"
