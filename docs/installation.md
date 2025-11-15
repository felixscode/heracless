# Installation

## From PyPI (Recommended)

The easiest way to install Heracless is from PyPI:

```bash
pip install heracless
```

---

## From Source

If you want the latest development version or want to contribute:

```bash
git clone https://github.com/felixscode/heracless.git
cd heracless
pip install -e .
```

---

## Requirements

| Python Version | Status |
|---------------|--------|
| 3.10 - 3.13 | Fully Supported |
| 3.9 and below | Not Supported |

**Dependencies:**

Heracless has minimal dependencies:

- `PyYAML` - YAML parsing
- `black` - Code formatting for generated stubs
- `art` - ASCII art for CLI

These are automatically installed when you install Heracless.

**Note:** Prebuilt Rust wheels are available for Linux, macOS, and Windows. No Rust installation required!

---

## Development Installation

If you want to contribute or run tests:

```bash
# Clone the repository
git clone https://github.com/felixscode/heracless.git
cd heracless

# Install with development dependencies
pip install -e .[dev]
```

This includes:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Static type checking
- `types-PyYAML` - Type stubs for PyYAML

---

## Verifying Installation

After installation, you can verify it works:

```bash
python -c "import heracless; print(heracless.__version__)"
```

Or use the CLI tool:

```bash
python -m heracless --help
```

---

## Next Steps

Now that you have Heracless installed, head over to the [Quick Start](quick-start.md) guide to create your first config!
