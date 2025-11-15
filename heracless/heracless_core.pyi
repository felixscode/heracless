"""Type stubs for heracless_core Rust extension module"""

def generate_python_stubs(config_path: str, frozen: bool) -> str:
    """
    Generate Python type stubs from YAML configuration

    Args:
        config_path: Path to the YAML configuration file
        frozen: Whether to generate frozen dataclasses

    Returns:
        Python stub code as a string
    """
    ...

def parse_yaml_to_json(config_path: str) -> str:
    """
    Parse YAML file and convert to JSON string

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        JSON string representation of the YAML data
    """
    ...
