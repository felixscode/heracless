# Usage

## Basic Configuration Loading

```python
from myproject.load_config import load_config

# Load with defaults (frozen, with stub generation)
config = load_config()

# Access nested values with autocomplete
db_url = f"{config.database.host}:{config.database.port}"
```

---

## Mutable Configuration

```python
# Load mutable config for testing or dynamic updates
config = load_config(frozen=False)

# Modify values (only works with frozen=False)
config.database.host = "192.168.1.100"
```

With `frozen=False` the dataclasses are regular mutable dataclasses, and the generated stub declares them with a plain `@dataclass`.

---

## Lists and Empty Files

YAML lists are loaded as tuples, so they stay immutable as well:

```yaml
ports: [8080, 8081]
```

```python
config.ports  # (8080, 8081), typed as tuple[int, ...]
```

An empty config file (or one that only contains comments) loads as `None`.

---

## How YAML Maps to Types

YAML is resolved like PyYAML's `full_load` (YAML 1.1):

- `yes`/`no`/`on`/`off` are booleans, `017` is octal
- unquoted dates and timestamps become `datetime.date` / `datetime.datetime` (with timezone if given)
- anchors, aliases and merge keys (`<<`) are supported
- only a single document per file is supported; custom or unsupported tags (e.g. `!!python/object`, `!!binary`) are rejected

For example, this config:

```yaml
release: 2024-05-01
debug: off
ports: [8080, 8081]
mixed: [1, two, 3.5]
tags: []
servers:
  - name: alpha
    port: 8080
  - name: beta
    weight: 0.5
HTTPServer:
  apiKey: abc
  class: fast
  1st: true
```

generates these classes:

```python
@dataclass(frozen=True)
class Config:
    release: datetime.date
    debug: bool
    ports: tuple[int, ...]
    mixed: tuple[float | str, ...]
    tags: tuple[typing.Any, ...]
    servers: tuple[ServersItem, ...]
    http_server: HttpServer


@dataclass(frozen=True)
class ServersItem:
    name: str
    port: int | None
    weight: float | None


@dataclass(frozen=True)
class HttpServer:
    api_key: str
    class_: str
    _1st: bool
```

**Lists:** mixed lists become unions (ints mixed with floats widen to `float`), and an empty list is `tuple[typing.Any, ...]`. A list of mappings becomes a single item class whose fields are the keys of all items; a key missing from some items is typed `T | None` and is `None` at runtime (here `servers[0].weight` is `None`).

**Nested mappings:** each mapping gets a class named after its key. An empty mapping becomes a class without fields. If two mappings would get the same class name, they share the class when their structure is identical; otherwise the name is disambiguated with the parent's name (e.g. `other.server` -> `OtherServer`) or a number. A nested key called `config` gets the class `Config2`, since `Config` is the root.

**Attribute names:** keys are converted to snake_case, with acronyms handled (`bill-to` -> `bill_to`, `apiKey` -> `api_key`, `HTTPServer` -> `http_server`, `UPPER_CASE` -> `upper_case`). Python keywords get a trailing underscore (`class` -> `class_`), a leading digit gets an underscore prefix (`1st` -> `_1st`), and non-string keys are converted with `str()` first (`1` -> `_1`). Keys that collide after conversion get numbered suffixes: `my-key` and `my_key` become `my_key` and `my_key_1`.

---

## Helper Functions

### Converting to Dictionary

```python
from heracless import as_dict

config = load_config()
config_dict = as_dict(config)

# Now a regular Python dictionary (lists stay tuples)
print(config_dict["database"]["host"])
```

### Creating Config from Dictionary

```python
from heracless import from_dict

config_dict = {
    "database": {"host": "localhost", "port": 5432},
    "api": {"base_url": "https://api.example.com", "timeout": 30}
}

config = from_dict(config_dict, frozen=True)
print(config.database.host)  # localhost
```

Types are inferred the same way as for YAML files. Values that are not plain data, such as a `Path`, are kept as they are.

### Updating Configuration Values

```python
from heracless import mutate_config

config = load_config()

# Create a new config with updated value (immutable pattern)
new_config = mutate_config(config, "database.host", "production-db.example.com")

print(config.database.host)      # localhost (original unchanged)
print(new_config.database.host)  # production-db.example.com
```

An unknown field in the path raises `AttributeError`.

`as_dict`, `from_dict` and `mutate_config` are also importable from `heracless.utils`.

### Generating a Stub Without Loading

```python
from heracless import generate_stub

stub = generate_stub("config.yaml")  # the .pyi content as a string (None for an empty file)
```

---

## CLI Tool

Generate stub files and validate configs from the command line. The `heracless` command is installed with the package; `python -m heracless` works too.

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

`.yaml` and `.yml` files are accepted. Errors are printed to stderr with exit status 1.

---

## Type Checking with mypy

Heracless works seamlessly with mypy:

```python
from myproject.load_config import load_config

config = load_config()

# This will be caught by mypy:
# error: "Config" has no attribute "databse"; maybe "database"?  [attr-defined]
host = config.databse.host  # Typo!

# This works:
host = config.database.host
```

Run mypy to catch errors:

```bash
mypy src/
```
