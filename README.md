# Heracless

<div align="center">

![Heracless](https://images.unsplash.com/photo-1728246950251-d0ca4d99e927?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

**Type-safe YAML configuration management for Python**

Transform your YAML config files into strongly-typed Python dataclasses with full IDE autocomplete support

[![PyPI version](https://badge.fury.io/py/heracless.svg)](https://badge.fury.io/py/heracless)
[![Python Version](https://img.shields.io/pypi/pyversions/heracless)](https://pypi.org/project/heracless/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/felixscode/heracless/actions/workflows/test.yml/badge.svg)](https://github.com/felixscode/heracless/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/felixscode/heracless/branch/main/graph/badge.svg)](https://codecov.io/gh/felixscode/heracless)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

[Installation](#installation) • [Quick Start](#quick-start) • [Documentation](https://heracless.io/Documentation) • [Examples](#usage-examples)

</div>

---

## Why Heracless?

Stop wrestling with dictionaries and string keys. Heracless automatically converts your YAML configuration files into Python dataclasses with **full type safety** and **IDE autocomplete support**.

```python
# WITHOUT Heracless - prone to typos, no autocomplete
config = yaml.load(open("config.yaml"))
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
- **Simple API** - One function to load configs, helper utilities included
- **Modern Python** - Supports Python 3.10, 3.11, 3.12, 3.13, 3.14
- **Minimal Dependencies** - Only PyYAML required for core functionality

---

## Installation

### From PyPI (Recommended)

```bash
pip install heracless
```

### From Source

```bash
git clone https://github.com/felixscode/heracless.git
cd heracless
pip install -e .
```

### Requirements

| Python Version | Status |
|---------------|--------|
| 3.10+ | Supported |
| 3.9 and below | Not supported |

**Dependencies:** PyYAML, black, art

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
    password: secret123

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
# load_config.pyi (auto-generated)
from dataclasses import dataclass
from typing import TypeVar

@dataclass(frozen=True)
class Credentials:
    username: str
    password: str

@dataclass(frozen=True)
class Database:
    host: str
    port: int
    name: str
    credentials: Credentials

@dataclass(frozen=True)
class Api:
    base_url: str
    timeout: int
    retries: int

@dataclass(frozen=True)
class Features:
    enable_caching: bool
    max_cache_size: int

@dataclass(frozen=True)
class Config:
    database: Database
    api: Api
    features: Features

Config = TypeVar("Config")
```

This stub file enables **full IDE autocomplete and type checking** without any manual work!

---

## Comparison with Alternatives

| Feature | Heracless | Plain YAML | Pydantic | OmegaConf |
|---------|-----------|------------|----------|-----------|
| Auto type generation | Yes | No | Manual | Manual |
| IDE autocomplete | Full | None | With manual schemas | Limited |
| Type checking (mypy) | Yes | No | Yes | Partial |
| Zero boilerplate | Yes | Yes | No | Partial |
| Immutable configs | Default | No | Optional | Optional |
| Learning curve | Low | Low | Medium | Medium |
| Config file format | YAML | YAML | Multiple | Multiple |

**Why choose Heracless?**
- **Automatic stub generation**: No manual dataclass or schema definitions needed
- **Focused simplicity**: Does one thing exceptionally well - YAML to typed dataclass
- **Development experience**: Catches config errors before you run your code
- **Minimal overhead**: Lightweight with minimal dependencies

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
from heracless.utils.helper import as_dict

config = load_config()
config_dict = as_dict(config)

# Now a regular Python dictionary
print(config_dict["database"]["host"])  # localhost
```

### Creating Config from Dictionary

```python
from heracless.utils.helper import from_dict

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
print(config.database.host)  # localhost (with type checking!)
```

### Updating Configuration Values

```python
from heracless.utils.helper import mutate_config

config = load_config()

# Create a new config with updated value (immutable pattern)
new_config = mutate_config(config, "database.host", "production-db.example.com")

print(config.database.host)      # localhost (original unchanged)
print(new_config.database.host)  # production-db.example.com
```

### CLI Tool Usage

Heracless includes a CLI tool for generating stub files and validating configs:

```bash
# Generate stub file from config
python -m heracless config.yaml --parse types.pyi

# Dry run (validate config without generating files)
python -m heracless config.yaml --dry

# Show help
python -m heracless --help
```

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

### Common Issues

#### **Issue: `ModuleNotFoundError: No module named 'heracless'`**

**Solution:** Install heracless in your environment:
```bash
pip install heracless
```

#### **Issue: Stub file not generated**

**Solution:** Ensure `stub_dump=True` in your `load_config()` function:
```python
def load_config(..., stub_dump: bool = True) -> Config:
    file_path = Path(__file__).resolve() if stub_dump else None
    return _load_config(config_path, file_path, frozen=frozen)
```

#### **Issue: IDE not showing autocomplete**

**Solutions:**
1. Ensure the `.pyi` file exists next to your `load_config.py`
2. Reload your IDE/editor window
3. Check that your language server is running (VSCode: check Python extension)
4. For PyCharm: File → Invalidate Caches → Restart

#### **Issue: `TypeError: 'Config' object is immutable`**

**Solution:** This is by design (frozen dataclass). To modify configs:
- Use `mutate_config()` helper to create updated copies
- Or load with `frozen=False` for mutable configs (not recommended)

#### **Issue: YAML parsing errors**

**Solution:** Ensure your YAML is valid:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

#### **Issue: Type hints not working with mypy**

**Solution:** Ensure mypy can find the generated `.pyi` file and you're using proper type imports:
```python
from typing import TypeVar
Config = TypeVar("Config")  # Required for type checking
```

---

## API Reference

### Core Functions

#### `load_config(config_path, file_path, frozen)`

Load a YAML configuration file and convert it to a typed dataclass.

**Parameters:**
- `config_path` (Path | str): Path to the YAML configuration file
- `file_path` (Path | str | None): Path where stub file should be generated (None to skip)
- `frozen` (bool): Whether the resulting dataclass should be immutable (default: True)

**Returns:** Config dataclass with attributes matching your YAML structure

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `yaml.YAMLError`: If YAML file is malformed

---

### Helper Functions

#### `mutate_config(config, name, value)`

Create a new config with an updated value (immutable pattern).

```python
from heracless.utils.helper import mutate_config

config = load_config()
new_config = mutate_config(config, "database.port", 3306)
```

#### `as_dict(config)`

Convert a Config dataclass to a nested dictionary.

```python
from heracless.utils.helper import as_dict

config = load_config()
config_dict = as_dict(config)  # Returns: dict
```

#### `from_dict(config_dict, frozen)`

Create a Config dataclass from a dictionary.

```python
from heracless.utils.helper import from_dict

config_dict = {"database": {"host": "localhost"}}
config = from_dict(config_dict, frozen=True)
```

---

## Performance & Limitations

### Performance

- **Config loading:** Typically < 10ms for configs under 1000 lines
- **Stub generation:** One-time cost, only runs when config structure changes
- **Memory:** Minimal overhead compared to plain dictionaries
- **Type checking:** Zero runtime overhead (all checking happens at development time)

### Limitations

- **YAML only:** Currently only supports YAML format (JSON, TOML support planned)
- **Structure changes:** Stub file regeneration required when YAML structure changes
- **Complex types:** Advanced YAML features (anchors, tags) may have limited type support
- **Circular references:** Not supported in config structures
- **Dynamic keys:** Dictionary-style configs with dynamic keys are not fully typed

### Best Practices

- Keep config files under 5000 lines for optimal performance
- Use nested structures to organize related settings
- Commit generated `.pyi` files to version control
- Use `frozen=True` (default) to prevent accidental modifications
- Regenerate stubs after changing config structure
- Avoid using YAML anchors/aliases for critical type-checked fields
- Don't modify generated `.pyi` files manually (changes will be overwritten)

---

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/felixscode/heracless.git
cd heracless

# Install with development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run type checking
mypy heracless

# Run code formatting
black heracless tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=heracless --cov-report=html

# Run specific test file
pytest tests/test_config.py
```

### Development Dependencies

Install development dependencies with:

```bash
pip install -e .[dev]
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Static type checking
- `types-PyYAML` - Type stubs for PyYAML

### Documentation Development

To work on the documentation web app:

```bash
pip install -e .[doc]
streamlit run heracless/wapp/About.py
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass (`pytest`)
6. **Run** type checking (`mypy heracless`)
7. **Format** code (`black heracless tests`)
8. **Commit** your changes (`git commit -m 'Add amazing feature'`)
9. **Push** to your branch (`git push origin feature/amazing-feature`)
10. **Open** a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Maximum line length: 120 characters (configured in black)
- Write docstrings for public APIs
- Add tests for new features

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

### Current Version: 0.4.0

### Planned Features

- [ ] **Config variants** - Support for environment-specific configs (dev/staging/prod)
- [ ] **JSON support** - Load JSON configuration files
- [ ] **TOML support** - Load TOML configuration files
- [ ] **Config validation** - Built-in validation rules
- [ ] **Environment variable interpolation** - `${ENV_VAR}` syntax in YAML
- [ ] **Config merging** - Combine multiple config files
- [ ] **Schema export** - Export JSON Schema from configs
- [ ] **Migration tools** - Helper utilities for config updates

### Completed

- [x] None type support
- [x] Web application for interactive config generation
- [x] CLI tool for stub generation
- [x] Frozen dataclass support
- [x] Helper utilities (mutate_config, as_dict, from_dict)

Want to see a feature? [Open an issue](https://github.com/felixscode/heracless/issues) to discuss!

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
- **Documentation:** [heracless.io/Documentation](https://heracless.io/Documentation)
- **GitHub Repository:** [github.com/felixscode/heracless](https://github.com/felixscode/heracless)
- **Project Website:** [heracless.io](https://heracless.io)
- **Issues & Support:** [GitHub Issues](https://github.com/felixscode/heracless/issues)

---

## Author

**Felix Schelling**

- GitHub: [@felixscode](https://github.com/felixscode)
- Website: [felixschelling.de](https://felixschelling.de)
- Email: felix.schelling@protonmail.com

---

<div align="center">

**If Heracless helps your project, consider giving it a star on GitHub!**

[Back to Top](#heracless)

</div>
