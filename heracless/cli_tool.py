import argparse
import os
import sys
from typing import Optional

from art import text2art
from yaml import full_load

from heracless.fight import dump_in_console, dump_in_file


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments and returns them as a Namespace object.

    If --help or --version is provided, it prints the ASCII art and exits the program.
    """
    parser = argparse.ArgumentParser(
        description="Heracless Client Tool",
        usage="""heracless [-h] cfg_dir [--parse [PARSE]] [--dry] [--version]""",
    )
    parser.add_argument("cfg_dir", help="Path to the configuration file", type=str)
    parser.add_argument("--parse", "-p", help="path to where to parse the input as a python file ", type=str)
    parser.add_argument("--dry", "-d", action="store_true", help="Dry run")
    parser.add_argument("--version", action="version", version="Heracless 0.2")

    if "-h" in sys.argv or "--help" in sys.argv or "--version" in sys.argv:
        my_text = "Heracless Client Tool"
        ascii_art = text2art(my_text)
        print(ascii_art)
    return parser.parse_args()


def run_cli() -> None:
    """
    Parses command line arguments and runs the main function based on the arguments.

    If --dry is provided, it runs the main function with dump_func set to dump_in_console.
    If --parse is provided, it runs the main function with dump_func set to dump_in_file.
    """
    args = parse_args()
    cfg_path: str = args.cfg_dir

    if not os.path.exists(cfg_path) or not cfg_path.endswith(".yaml"):
        print("Config file does not exist or is not a YAML file.")

    if args.dry:
        main(
            cfg_dir=cfg_path,
            dump_dir=None,
            dump_func=dump_in_console,
            yaml_load_func=full_load,
            make_dir=False,
            frozen=True,
        )
    elif args.parse:
        dump_path: Optional[str] = args.parse
        if not os.path.exists(dump_path) or not dump_path.endswith(".py"):
            print("Dump file does not exist or is not a Python file.")
        main(
            cfg_dir=cfg_path,
            dump_dir=dump_path,
            dump_func=dump_in_file,
            yaml_load_func=full_load,
            make_dir=False,
            frozen=True,
        )


if __name__ == "__main__":
    run_cli()
