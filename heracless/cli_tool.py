"""Command line interface: ``heracless CONFIG [--parse STUB | --dry]`` (or ``python -m heracless``)."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

from heracless.fight import generate_stub, load_config
from heracless.utils.exceptions import HeraclessError

BANNER = r"""
 _   _                           _
| | | |  ___  _ __   __ _   ___ | |  ___  ___  ___
| |_| | / _ \| '__| / _` | / __|| | / _ \/ __|/ __|
|  _  ||  __/| |   | (_| || (__ | ||  __/\__ \\__ \
|_| |_| \___||_|    \__,_| \___||_| \___||___/|___/
"""

YAML_SUFFIXES = (".yaml", ".yml")
STUB_SUFFIXES = (".py", ".pyi")


def _version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("heracless")
    except PackageNotFoundError:  # pragma: no cover - running from a source tree without metadata
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="heracless",
        description=f"{BANNER}\nTurn a YAML config into typed Python dataclasses.\n\n"
        "Without options, the generated type stub is printed to stdout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("cfg_dir", metavar="CONFIG", help="path to the YAML config file")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--parse", "-p", metavar="STUB", help="write the type stub to STUB (a .py suffix is replaced by .pyi)"
    )
    mode.add_argument("--dry", "-d", action="store_true", help="load the config and print it, writing nothing")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_version()}")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments (``sys.argv[1:]`` by default)."""
    return build_parser().parse_args(argv)


def _error(message: str) -> int:
    print(f"heracless: error: {message}", file=sys.stderr)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    args = parse_args(argv)
    cfg_path = Path(args.cfg_dir)

    if cfg_path.suffix not in YAML_SUFFIXES:
        return _error(f"{cfg_path} is not a YAML file (expected a {' or '.join(YAML_SUFFIXES)} suffix)")
    if not cfg_path.is_file():
        return _error(f"config file {cfg_path} does not exist")
    if args.parse and Path(args.parse).suffix not in STUB_SUFFIXES:
        return _error("the stub file must be a Python file (.py or .pyi)")

    try:
        if args.dry:
            print(f"Loaded config: {load_config(cfg_path, None)}")
        elif args.parse:
            stub_path = Path(args.parse).with_suffix(".pyi")
            if load_config(cfg_path, stub_path) is None:
                return _error(f"{cfg_path} is empty, no stub written")
            print(f"Config generated and written to {stub_path}")
        else:
            stub = generate_stub(cfg_path)
            if stub is None:
                return _error(f"{cfg_path} is empty")
            sys.stdout.write(stub)
    except (HeraclessError, OSError) as e:
        return _error(str(e))
    return 0


def run_cli() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    run_cli()
