from pathlib import Path

_TEMPLATE_PATH = Path(__file__).parent / "load_func_template.py"


def insert_path_into_load_config_template(config_dir: Path | str) -> list[str]:
    """Return the lines of the ``load_config`` template with ``CONFIG_YAML_PATH`` pointing at ``config_dir``."""
    lines: list[str] = []
    with open(_TEMPLATE_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(("CONFIG_YAML_PATH:", "CONFIG_YAML_PATH =")):
                # repr() yields a valid literal even for Windows paths ("C:\new" must not become a newline).
                lines.append(f"CONFIG_YAML_PATH: Optional[Path] = Path({str(config_dir)!r})\n")
            else:
                lines.append(line)
    return lines


def dump_template_to_file(config_path: Path | str, file_path: Path | str, force: bool = False) -> None:
    """Write a ready-to-use ``load_config`` module to ``file_path`` (kept as is if it exists, unless ``force``)."""
    file_path = Path(file_path)
    if not force and file_path.exists():
        return
    file_path.write_text("".join(insert_path_into_load_config_template(config_path)), encoding="utf-8")
