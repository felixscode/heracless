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

---

## Helper Functions

### Converting to Dictionary

```python
from heracless.utils.helper import as_dict

config = load_config()
config_dict = as_dict(config)

# Now a regular Python dictionary
print(config_dict["database"]["host"])
```

### Creating Config from Dictionary

```python
from heracless.utils.helper import from_dict

config_dict = {
    "database": {"host": "localhost", "port": 5432},
    "api": {"base_url": "https://api.example.com", "timeout": 30}
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

---

## CLI Tool

Generate stub files and validate configs from the command line:

```bash
# Generate stub file from config
python -m heracless config.yaml --parse types.pyi

# Dry run (validate config without generating files)
python -m heracless config.yaml --dry

# Show help
python -m heracless --help
```

---

## Type Checking with mypy

Heracless works seamlessly with mypy:

```python
from myproject.load_config import load_config

config = load_config()

# This will be caught by mypy:
# error: "Config" has no attribute "databse"
host = config.databse.host  # Typo!

# This works:
host = config.database.host
```

Run mypy to catch errors:

```bash
mypy src/
```
