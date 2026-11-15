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

- `config_path` - Path to the YAML configuration file (`.yaml` or `.yml`)
- `file_path` - Path where stub file should be generated (`None` to skip). Its suffix is replaced by `.pyi`, so passing `Path(__file__)` of your loader module works. The file is only rewritten when its content changes.
- `frozen` - Whether the resulting dataclass should be immutable (default: `True`)

**Returns:** Config dataclass with attributes matching your YAML structure, or `None` if the file is empty (or only contains comments). Lists are returned as tuples.

**Raises:**

- `heracless.DirectoryError` - If the config file or the stub's directory doesn't exist (subclass of `FileNotFoundError`). A missing config file is not created.
- `heracless.YamlSyntaxError` - If the YAML file is malformed, uses custom or unsupported tags, contains more than one document, nests deeper than 128 levels or expands aliases to more than 1,000,000 nodes (subclass of `ValueError`; the message includes line and column for syntax errors)
- `heracless.ConfigError` - If the top level of the YAML is not a mapping (subclass of `ValueError`)

---

### `generate_stub()`

Return the type stub for a config file without building the config objects or writing any file.

```python
from heracless import generate_stub

stub = generate_stub(
    config_path: Path | str,
    frozen: bool = True
) -> str | None
```

**Parameters:**

- `config_path` - Path to the YAML configuration file
- `frozen` - Whether the stub declares `@dataclass(frozen=True)` or plain `@dataclass` (default: `True`)

**Returns:** The `.pyi` content as a string, or `None` if the file is empty

**Raises:** The same errors as `load_config()`

---

## Exceptions

All exceptions are importable from `heracless` and derive from `heracless.HeraclessError`.

| Exception | Base classes | Raised when |
|-----------|--------------|-------------|
| `DirectoryError` | `HeraclessError`, `FileNotFoundError` | The config file or the stub's directory doesn't exist |
| `YamlSyntaxError` | `HeraclessError`, `ValueError` | The file is not valid YAML or uses unsupported YAML features |
| `ConfigError` | `HeraclessError`, `ValueError` | The top level of the YAML is not a mapping |

---

## Helper Functions

`mutate_config`, `as_dict` and `from_dict` are importable from `heracless` (and from `heracless.utils`).

### `mutate_config()`

Create a new config with an updated value (immutable pattern).

```python
from heracless import mutate_config

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

**Returns:** New config object with updated value (the original is unchanged)

**Raises:** `AttributeError` if the path refers to a field that doesn't exist

---

### `as_dict()`

Convert a Config dataclass to a nested dictionary.

```python
from heracless import as_dict

config_dict = as_dict(config: Config)
```

**Parameters:**

- `config` - Config object to convert

**Returns:** Dictionary representation (lists stay tuples)

---

### `from_dict()`

Create a Config dataclass from a dictionary.

```python
from heracless import from_dict

config = from_dict(
    config_dict: dict,
    frozen: bool = True
)
```

**Parameters:**

- `config_dict` - Dictionary to convert
- `frozen` - Whether to make the config immutable (default: `True`)

**Returns:** Config dataclass. Types are inferred the same way as for YAML files; values that are not plain data (e.g. a `Path`) are kept as they are.

---

### `__version__`

`heracless.__version__` holds the installed version as a string.

---

## CLI Tool

```bash
heracless CONFIG_PATH [OPTIONS]
python -m heracless CONFIG_PATH [OPTIONS]
```

**Arguments:**

- `CONFIG_PATH` - Path to YAML config file (`.yaml` or `.yml`)

Without options, the generated stub is printed to stdout.

**Options:**

- `--parse`, `-p OUTPUT_PATH` - Write the stub file to OUTPUT_PATH (a `.py` suffix is replaced by `.pyi`)
- `--dry`, `-d` - Load the config and print it without writing files
- `--version` - Show the version
- `--help` - Show help message

`--parse` and `--dry` are mutually exclusive. Errors are printed to stderr and the command exits with status 1.
