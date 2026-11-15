# Installation

## From PyPI (Recommended)

The easiest way to install Heracless is from PyPI:

```bash
pip install heracless
```

---

## From Source

If you want the latest development version or want to contribute. Building from source compiles the Rust extension with [maturin](https://www.maturin.rs/), so you need a Rust toolchain (1.83+, e.g. via [rustup](https://rustup.rs/)):

```bash
git clone https://github.com/felixscode/heracless.git
cd heracless
pip install -e .
```

---

## Requirements

| Python Version | Status |
|---------------|--------|
| 3.10 - 3.14 | Fully Supported |
| 3.9 and below | Not Supported |

**Dependencies:**

Heracless has no runtime dependencies. YAML parsing, type inference and stub generation are done by its compiled Rust extension.

**Note:** Prebuilt wheels are available for Linux (x86_64, aarch64), macOS (universal2) and Windows (x64). They use Python's stable ABI, so one wheel per platform covers Python 3.10 and newer. No Rust installation is needed unless pip has to build from the source distribution.

---

## Development Installation

If you want to contribute or run tests:

```bash
# Clone the repository
git clone https://github.com/felixscode/heracless.git
cd heracless

# Install with development dependencies (builds the Rust extension, needs Rust)
pip install -e ".[dev]"
```

This includes:

- `maturin` - Builds the Rust extension
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Static type checking
- `PyYAML` and `types-PyYAML` - Used only by the tests, to check that YAML is resolved the same way as PyYAML

Run the checks with:

```bash
pytest
cargo test
mypy heracless
cargo fmt
cargo clippy --all-targets --features python
```

---

## Verifying Installation

After installation, you can verify it works:

```bash
python -c "import heracless; print(heracless.__version__)"
```

Or use the CLI tool:

```bash
heracless --version
heracless --help
```

`python -m heracless --help` works as well.

---

## Next Steps

Now that you have Heracless installed, head over to the [Quick Start](quick-start.md) guide to create your first config!
