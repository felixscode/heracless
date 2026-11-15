<div align="center">

# Heracless


![Heracless](https://images.unsplash.com/photo-1728246950251-d0ca4d99e927?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

**Type-safe YAML configuration management for Python**

Transform your YAML config files into strongly-typed Python dataclasses with full IDE autocomplete support

[![PyPI version](https://badge.fury.io/py/heracless.svg)](https://badge.fury.io/py/heracless)
[![Python Version](https://img.shields.io/pypi/pyversions/heracless)](https://pypi.org/project/heracless/)
[![Rust](https://img.shields.io/badge/Rust-1.83+-orange?logo=rust)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/felixscode/heracless/actions/workflows/test.yml/badge.svg)](https://github.com/felixscode/heracless/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/felixscode/heracless/branch/main/graph/badge.svg)](https://codecov.io/gh/felixscode/heracless)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://heracless.io)

[Installation](#installation) • [Quick Start](#quick-start) • [Documentation](https://heracless.io) • [Examples](#usage-examples)

</div>

---

## Why Heracless?

Stop wrestling with dictionaries and string keys. Heracless automatically converts your YAML configuration files into Python dataclasses with **full type safety** and **IDE autocomplete support**.
The YAML parsing, type inference and stub generation run in a Rust core: for a ~100 KB config they take around 10 ms, and most of the remaining load time is spent creating the dataclass objects in Python.

```python
# WITHOUT Heracless - prone to typos, no autocomplete
config = yaml.safe_load(open("config.yaml"))
db_host = config["database"]["host"]  # Runtime errors waiting to happen
db_port = config["databse"]["port"]   # Typo goes unnoticed!

# WITH Heracless - type-safe, autocomplete, catch errors at write-time
config = load_config()
db_host = config.database.host  # Autocomplete works!
db_port = config.database.port  # Typos caught by IDE/mypy
```

---

## Features

- **Automatic Type Generation** - Generates `.pyi` stub files for full IDE support
- **Type Safety** - Catch configuration errors at development time, not runtime
- **Zero Boilerplate** - No manual dataclass definitions needed
- **IDE Autocomplete** - Full IntelliSense/autocomplete for all config values
- **Immutable by Default** - Frozen dataclasses prevent accidental modifications
- **Rust Core, No Dependencies** - YAML parsing, type inference and stub generation are implemented in Rust; the package has no runtime Python dependencies

---

## Installation

### From PyPI (Recommended)

```bash
pip install heracless
```

### From Source

Building from source compiles the Rust extension with [maturin](https://www.maturin.rs/), so you need a Rust toolchain (1.83+, e.g. via [rustup](https://rustup.rs/)):

```bash
git clone https://github.com/felixscode/heracless.git
cd heracless
pip install -e .
```

### Requirements

| Python Version | Status |
|---------------|--------|
| 3.10 - 3.14 | Fully Supported |
| 3.9 and below | Not Supported |

**Dependencies:** none at runtime.

**Note:** Prebuilt wheels are available for Linux (x86_64, aarch64), macOS (universal2) and Windows (x64). They use Python's stable ABI, so one wheel per platform covers Python 3.10 and newer. No Rust installation is needed unless pip has to build from the source distribution.

---

## Quick Start

### 1. Create your configuration file

Create a `config.yaml` file with your settings:

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  name: myapp_db
  credentials:
    username: admin
    password: secret123 # don't use this in production

api:
  base_url: https://api.example.com
  timeout: 30
  retries: 3

features:
  enable_caching: true
  max_cache_size: 1000
```

### 2. Set up the config loader

Create a `load_config.py` file in your project:

```python
# src/myproject/load_config.py
from pathlib import Path
from typing import TypeVar
from heracless import load_config as _load_config

# Point to your config file
CONFIG_YAML_PATH = Path(__file__).parent.parent / "config.yaml"

Config = TypeVar("Config")

def load_config(config_path: Path | str = CONFIG_YAML_PATH,
                frozen: bool = True,
                stub_dump: bool = True) -> Config:
    """Load configuration and generate type stubs."""
    file_path = Path(__file__).resolve() if stub_dump else None
    return _load_config(config_path, file_path, frozen=frozen)
```

### 3. Use your config with full type safety

```python
# src/myproject/main.py
from myproject.load_config import load_config

# Load config - first run generates load_config.pyi with types!
config = load_config()

# Access config with autocomplete and type checking
print(f"Connecting to {config.database.host}:{config.database.port}")
print(f"Database: {config.database.name}")
print(f"API URL: {config.api.base_url}")
print(f"Caching enabled: {config.features.enable_caching}")
```

**Output:**
```
Connecting to localhost:5432
Database: myapp_db
API URL: https://api.example.com
Caching enabled: True
```

### Generated Type Stub Example

After the first run, Heracless automatically generates a `load_config.pyi` file:

```python
# load_config.pyi
# This file was generated by heracless. Do not edit it by hand:
# it is rewritten whenever the config is loaded with stub generation enabled.
import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    database: Database
    api: Api
    features: Features


@dataclass(frozen=True)
class Database:
    host: str
    port: int
    name: str
    credentials: Credentials


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class Api:
    base_url: str
    timeout: int
    retries: int


@dataclass(frozen=True)
class Features:
    enable_caching: bool
    max_cache_size: int


def load_config(
    config_path: pathlib.Path | str | None = ...,
    frozen: bool = ...,
    stub_dump: bool = ...,
) -> Config: ...
```

This stub file enables **full IDE autocomplete and type checking**. It also types your `load_config()` function, so `load_config()` returns `Config` for mypy and your IDE. The output is deterministic, and the file is only rewritten when its content changes.

#### How YAML values are typed

- Scalars follow YAML 1.1 (like PyYAML's `full_load`): `yes`/`no`/`on`/`off` are booleans, unquoted dates and timestamps become `datetime.date`/`datetime.datetime`, `017` is octal. Anchors, aliases and merge keys (`<<`) are supported.
- Lists become tuples, e.g. `tuple[int, ...]`. Mixed lists become unions (`tuple[int | str, ...]`; ints mixed with floats widen to `float`), an empty list is `tuple[typing.Any, ...]`.
- A list of mappings becomes one item class (e.g. `ServersItem`) with the keys of all items. Keys missing from some items are typed `T | None` and are `None` at runtime.
- Keys are converted to snake_case attribute names: `bill-to` -> `bill_to`, `apiKey` -> `api_key`, `HTTPServer` -> `http_server`. Python keywords get a trailing underscore (`class` -> `class_`), a leading digit gets an underscore prefix (`1st` -> `_1st`), and keys that collide after conversion get `_1`, `_2`, ... suffixes.


---

## Usage Examples

### Basic Configuration Loading

```python
from myproject.load_config import load_config

# Load with defaults (frozen, with stub generation)
config = load_config()

# Access nested values with autocomplete
db_url = f"{config.database.host}:{config.database.port}"
```

### Mutable Configuration

```python
# Load mutable config for testing or dynamic updates
config = load_config(frozen=False)

# Modify values (only works with frozen=False)
config.database.host = "192.168.1.100"
```

### Converting to Dictionary

```python
from heracless import as_dict

config = load_config()
config_dict = as_dict(config)

# Now a regular Python dictionary (lists stay tuples)
print(config_dict["database"]["host"])  # localhost
```

### Creating Config from Dictionary

```python
from heracless import from_dict

config_dict = {
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "api": {
        "base_url": "https://api.example.com",
        "timeout": 30
    }
}

config = from_dict(config_dict, frozen=True)
print(config.database.host)  # localhost
```

### Updating Configuration Values

```python
from heracless import mutate_config

config = load_config()

# Create a new config with updated value (immutable pattern)
new_config = mutate_config(config, "database.host", "production-db.example.com")

print(config.database.host)      # localhost (original unchanged)
print(new_config.database.host)  # production-db.example.com
```

### Generating a Stub Without Loading

```python
from heracless import generate_stub

stub = generate_stub("config.yaml")  # the .pyi content as a string (None for an empty file)
```

### CLI Tool Usage

Heracless installs a `heracless` command for generating stub files and validating configs (`python -m heracless` works too):

```bash
# Print the generated stub to stdout
heracless config.yaml

# Write the stub to a file (a .py suffix is replaced by .pyi)
heracless config.yaml --parse types.pyi

# Dry run (load and print the config without writing files)
heracless config.yaml --dry

# Show version / help
heracless --version
heracless --help
```

`.yaml` and `.yml` files are accepted. Errors are printed to stderr and the command exits with status 1.

---

## Project Structure Example

Here's a recommended project structure:

```
my_project/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── main.py
│       └── config/
│           ├── __init__.py
│           ├── load_config.py      # Your config loader
│           └── load_config.pyi     # Auto-generated types
├── config/
│   ├── config.yaml                 # Main config
│   ├── config.dev.yaml             # Development overrides
│   └── config.prod.yaml            # Production overrides
├── tests/
│   └── test_config.py
├── pyproject.toml
└── README.md
```

---

## Troubleshooting




### **Issue: IDE not showing autocomplete**

**Solutions:**
1. Ensure the `.pyi` file exists next to your `load_config.py`
2. Reload your IDE/editor window
3. Check that your language server is running (VSCode: check Python extension)
4. For PyCharm: File → Invalidate Caches → Restart

#### **Issue: `dataclasses.FrozenInstanceError: cannot assign to field 'host'`**

**Solution:** This is by design (frozen dataclass). To modify configs:
- Use `mutate_config()` helper to create updated copies
- Or load with `frozen=False` for mutable configs (not recommended)

#### **Issue: YAML parsing errors**

**Solution:** Heracless raises `heracless.YamlSyntaxError` with the line and column of the problem. You can check a file from the command line:
```bash
# Validate YAML syntax (prints the error and exits with status 1 if invalid)
heracless config.yaml --dry
```

Only a single YAML document per file is supported, and custom or unsupported tags (e.g. `!!python/object`, `!!binary`) are rejected.

---

## API Reference

### Core Functions

#### `load_config(config_path, file_path, frozen)`

Load a YAML configuration file and convert it to a typed dataclass.

**Parameters:**
- `config_path` (Path | str): Path to the YAML configuration file
- `file_path` (Path | str | None): Path where stub file should be generated (None to skip)
- `frozen` (bool): Whether the resulting dataclass should be immutable (default: True)

**Returns:** Config dataclass with attributes matching your YAML structure, or `None` if the file is empty (or only contains comments)

**Raises:**
- `heracless.DirectoryError` (a `FileNotFoundError`): If the config file or the stub's directory doesn't exist
- `heracless.YamlSyntaxError` (a `ValueError`): If the YAML file is malformed; the message includes line and column
- `heracless.ConfigError` (a `ValueError`): If the top level of the YAML is not a mapping

All three derive from `heracless.HeraclessError`.

#### `generate_stub(config_path, frozen)`

Return the `.pyi` stub for a config file as a string without writing anything (`None` if the file is empty).

---

### Helper Functions

#### `mutate_config(config, name, value)`

Create a new config with an updated value (immutable pattern). `name` is a dot-separated path; an unknown field raises `AttributeError`.

```python
from heracless import mutate_config

config = load_config()
new_config = mutate_config(config, "database.port", 3306)
```

#### `as_dict(config)`

Convert a Config dataclass to a nested dictionary.

```python
from heracless import as_dict

config = load_config()
config_dict = as_dict(config)  # Returns: dict
```

#### `from_dict(config_dict, frozen)`

Create a Config dataclass from a dictionary. Types are inferred the same way as for YAML files; values that are not plain data (e.g. a `Path`) are kept as they are.

```python
from heracless import from_dict

config_dict = {"database": {"host": "localhost"}}
config = from_dict(config_dict, frozen=True)
```

---

### Rust Crate

The engine is also a Rust library (the `heracless` crate in `src/`). The PyO3 bindings live behind the `python` cargo feature, which maturin enables for the Python package.

```rust
let doc = heracless::Document::load(path)?.expect("config is not empty");

// Python stub, as written by the Python package
let stub = heracless::codegen::python::generate_stub(&doc.schema, true);

// serde structs for using the config from Rust
let structs = heracless::codegen::rust::generate(&doc.schema);
```

`Document::from_str` parses a string instead of a file, and `heracless::generate_rust_types(config_path, output_path)` writes the generated structs to a file.

---

## Contributing

Contributions are welcome! Here's how you can help:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/felixscode/heracless.git
cd heracless

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run Rust tests
cargo test

# Run type checking
mypy heracless

# Format and lint the Rust code
cargo fmt
cargo clippy --all-targets --features python
```

Installing in editable mode builds the Rust extension with maturin, so a Rust toolchain (1.83+) is required. After changing Rust code, re-run `pip install -e ".[dev]"` to rebuild it.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=heracless --cov-report=html

# Run specific test file
pytest tests/test_load_config.py
```

### Development Dependencies

Install development dependencies with:

```bash
pip install -e ".[dev]"
```

This includes:
- `maturin` - Builds the Rust extension
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Static type checking
- `PyYAML` and `types-PyYAML` - Used only by the tests, to check that YAML is resolved the same way as PyYAML

### Documentation Development

To work on the documentation:

```bash
# Install documentation dependencies
pip install -e .[doc]

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```


### Reporting Issues

Found a bug or have a feature request? [Open an issue](https://github.com/felixscode/heracless/issues) on GitHub.

Please include:
- Heracless version (`pip show heracless`)
- Python version
- Operating system
- Minimal reproducible example
- Expected vs actual behavior

---

## Roadmap

### Current Version: 0.5.1

### Planned Features

- [ ] **Config variants** - Support for environment-specific configs (dev/staging/prod)
- [ ] **Environment variable interpolation** - `${ENV_VAR}` syntax in YAML

---

## License

Heracless is released under the **MIT License**. See [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2023 Felix Schelling

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

**TL;DR:** You can freely use, modify, and distribute this software, even for commercial purposes.

---

## Links & Resources

- **PyPI Package:** [pypi.org/project/heracless](https://pypi.org/project/heracless/)
- **Documentation:** [heracless.io](https://heracless.io)
- **GitHub Repository:** [github.com/felixscode/heracless](https://github.com/felixscode/heracless)
- **Issues & Support:** [GitHub Issues](https://github.com/felixscode/heracless/issues)

---

## Author

**Felix Schelling**

- GitHub: [@felixscode](https://github.com/felixscode)
- Website: [felixschelling.de](https://felixschelling.de)


---

<div align="center">

**If Heracless helps your project, consider giving it a star on GitHub!**

[Back to Top](#heracless)

</div>
