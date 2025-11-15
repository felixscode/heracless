# Quick Start

This guide will walk you through creating your first configuration with Heracless.

---

## 1. Create Your Configuration File

Create a `config.yaml` file with your settings:

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  name: myapp_db
  credentials:
    username: admin
    password: secret123  # don't use this in production

api:
  base_url: https://api.example.com
  timeout: 30
  retries: 3

features:
  enable_caching: true
  max_cache_size: 1000
```

---

## 2. Set Up the Config Loader

Create a `load_config.py` file in your project. This file will be your interface to load configurations:

```python
# src/myproject/load_config.py
from pathlib import Path
from typing import TypeVar
from heracless import load_config as _load_config

# Point to your config file
CONFIG_YAML_PATH = Path(__file__).parent.parent / "config.yaml"

Config = TypeVar("Config")

def load_config(
    config_path: Path | str = CONFIG_YAML_PATH,
    frozen: bool = True,
    stub_dump: bool = True
) -> Config:
    """Load configuration and generate type stubs."""
    file_path = Path(__file__).resolve() if stub_dump else None
    return _load_config(config_path, file_path, frozen=frozen)
```

**Configuration Parameters:**

- `config_path`: Path to your YAML config file
- `frozen`: If `True`, creates immutable config (default: `True`)
- `stub_dump`: If `True`, generates `.pyi` type stub file (default: `True`)

---

## 3. Use Your Config

Now you can use your config with full type safety:

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

---

## 4. Generated Type Stub

After the first run, Heracless automatically generates a `load_config.pyi` file next to your `load_config.py`:

```python
# load_config.pyi (auto-generated - do not edit manually!)
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
```

This stub file enables:

- **Full IDE autocomplete**
- **Type checking with mypy**
- **IntelliSense in VSCode, PyCharm, etc.**
- **Catch typos at development time**

---

## Project Structure

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

## Next Steps

- Learn about [advanced usage patterns](usage.md)
- Explore the [API reference](api-reference.md)
- Check out [troubleshooting tips](troubleshooting.md)

Congratulations! You've set up your first Heracless configuration.
