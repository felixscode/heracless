# Welcome to Heracless

**Type-safe YAML configuration management for Python**

Transform your YAML config files into strongly-typed Python dataclasses with full IDE autocomplete support.

[![PyPI version](https://badge.fury.io/py/heracless.svg)](https://badge.fury.io/py/heracless)
[![Python Version](https://img.shields.io/pypi/pyversions/heracless)](https://pypi.org/project/heracless/)
[![Rust](https://img.shields.io/badge/Rust-1.70+-orange?logo=rust)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/felixscode/heracless/actions/workflows/test.yml/badge.svg)](https://github.com/felixscode/heracless/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/felixscode/heracless/branch/main/graph/badge.svg)](https://codecov.io/gh/felixscode/heracless)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

---

## Why Heracless?

Stop wrestling with dictionaries and string keys. Heracless automatically converts your YAML configuration files into Python dataclasses with **full type safety** and **IDE autocomplete support**. Plus it's written in Rust for blazing-fast performance.

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
- **Rust-Powered Performance** - Native Rust backend for blazing-fast YAML parsing and stub generation

---

## Quick Example

Create a `config.yaml` file:

```yaml
database:
  host: localhost
  port: 5432
  name: myapp_db
```

Load it with full type safety:

```python
from myproject.load_config import load_config

config = load_config()
print(f"Connecting to {config.database.host}:{config.database.port}")
```

Heracless automatically generates type stubs, giving you:

- Full autocomplete in your IDE
- Type checking with mypy
- Runtime validation
- Zero boilerplate

---

## Background

Working with config files in Python can be a pain. There's Meta's [Hydra](https://hydra.cc/), which is a powerful tool for managing complex configurations. For simple projects, Hydra can be overkill.

So I created **Heracless**, to fight Hydra.

The name is a play on "Hercules" (who fought the Hydra in Greek mythology) and "less" (as in, less complexity than Hydra).

---

## License

Heracless is released under the **MIT License**. See [LICENSE](https://github.com/felixscode/heracless/blob/main/LICENSE) for details.

---

## Author

**Felix Schelling**

- GitHub: [@felixscode](https://github.com/felixscode)
- Website: [felixschelling.de](https://felixschelling.de)
- Email: felix.schelling@protonmail.com

Written with ❤️ in Mexico
