# API Reference

## Core Functions

### `load_config()`

Load a YAML configuration file and convert it to a typed dataclass.

```python
from heracless import load_config

config = load_config(
    config_path: Path | str,
    file_path: Path | str | None = None,
    frozen: bool = True
)
```

**Parameters:**

- `config_path` - Path to the YAML configuration file
- `file_path` - Path where stub file should be generated (`None` to skip)
- `frozen` - Whether the resulting dataclass should be immutable (default: `True`)

**Returns:** Config dataclass with attributes matching your YAML structure

**Raises:**

- `FileNotFoundError` - If config file doesn't exist
- `yaml.YAMLError` - If YAML file is malformed

---

## Helper Functions

### `mutate_config()`

Create a new config with an updated value (immutable pattern).

```python
from heracless.utils.helper import mutate_config

new_config = mutate_config(
    config: Config,
    name: str,
    value: Any
)
```

**Parameters:**

- `config` - Original config object
- `name` - Dot-separated path to the value (e.g., `"database.port"`)
- `value` - New value to set

**Returns:** New config object with updated value

---

### `as_dict()`

Convert a Config dataclass to a nested dictionary.

```python
from heracless.utils.helper import as_dict

config_dict = as_dict(config: Config)
```

**Parameters:**

- `config` - Config object to convert

**Returns:** Dictionary representation

---

### `from_dict()`

Create a Config dataclass from a dictionary.

```python
from heracless.utils.helper import from_dict

config = from_dict(
    config_dict: dict,
    frozen: bool = True
)
```

**Parameters:**

- `config_dict` - Dictionary to convert
- `frozen` - Whether to make the config immutable (default: `True`)

**Returns:** Config dataclass

---

## CLI Tool

```bash
python -m heracless CONFIG_PATH [OPTIONS]
```

**Arguments:**

- `CONFIG_PATH` - Path to YAML config file

**Options:**

- `--parse OUTPUT_PATH` - Generate stub file at OUTPUT_PATH
- `--dry` - Validate config without generating files
- `--help` - Show help message
