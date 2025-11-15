# Troubleshooting

## IDE Not Showing Autocomplete

**Symptoms:**
- No autocomplete for config attributes
- IDE doesn't recognize config structure

**Solutions:**

1. Ensure the `.pyi` file exists next to your `load_config.py`
2. Reload your IDE/editor window
3. Check that your language server is running (VSCode: check Python extension)
4. For PyCharm: `File` → `Invalidate Caches` → `Restart`

---

## Config Object is Immutable

**Error:**
```
TypeError: cannot assign to field 'host'
```

**Cause:** Config is frozen by default (immutable dataclass).

**Solutions:**

**Option 1:** Use `mutate_config()` helper (recommended)
```python
from heracless.utils.helper import mutate_config

config = load_config()
new_config = mutate_config(config, "database.host", "new-host")
```

**Option 2:** Load with `frozen=False` (not recommended for production)
```python
config = load_config(frozen=False)
config.database.host = "new-host"
```

---

## YAML Parsing Errors

**Error:**
```
yaml.scanner.ScannerError: ...
```

**Cause:** Invalid YAML syntax in config file.

**Solution:** Validate your YAML:

```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

Common issues:
- Incorrect indentation
- Missing colons
- Invalid characters
- Mixing tabs and spaces

---

## FileNotFoundError

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
```

**Solutions:**

1. Check the path in `CONFIG_YAML_PATH` is correct
2. Use absolute paths or `Path(__file__)` for relative paths:
   ```python
   CONFIG_YAML_PATH = Path(__file__).parent / "config.yaml"
   ```
3. Verify the config file exists:
   ```bash
   ls -la config.yaml
   ```

---

## Type Checking Not Working

**Symptoms:**
- mypy doesn't catch config typos
- No type errors for invalid attribute access

**Solutions:**

1. Ensure `.pyi` stub file is generated (set `stub_dump=True`)
2. Run mypy with correct configuration:
   ```bash
   mypy --strict src/
   ```
3. Check mypy is using the correct Python version:
   ```bash
   mypy --version
   ```

---

## Stub File Not Generated

**Cause:** `stub_dump=False` or `file_path=None`

**Solution:**
```python
def load_config(..., stub_dump: bool = True) -> Config:
    file_path = Path(__file__).resolve() if stub_dump else None
    return _load_config(config_path, file_path, frozen=frozen)
```

Ensure `stub_dump=True` (default).

---

## Still Having Issues?

If you encounter other problems:

1. Check the [GitHub Issues](https://github.com/felixscode/heracless/issues)
2. Open a new issue with:
   - Heracless version (`pip show heracless`)
   - Python version
   - Operating system
   - Minimal reproducible example
   - Expected vs actual behavior
