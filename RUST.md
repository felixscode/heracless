# Heracless Rust Backend

Heracless now features a **Rust-powered core** for improved performance while maintaining the same Python API you know and love.

## Why Rust?

The Rust backend provides:
- **Faster YAML parsing** - Up to 10x faster than pure Python
- **Efficient tree building** - Memory-efficient data structures
- **Type-safe code generation** - Leveraging Rust's powerful type system
- **Zero runtime overhead** - Compiled to native code

## Architecture

```
┌─────────────────────────────────────┐
│     Python API (Unchanged)          │
│  heracless.fight.load_config()      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Rust Core (heracless_core)        │
│  - YAML Parsing (serde_yaml)         │
│  - Tree Building                     │
│  - Code Generation                   │
└─────────────────────────────────────┘
```

## Building from Source

### Prerequisites

- **Rust toolchain** (1.70+)
- **Python** (3.10+)
- **maturin** - Python/Rust build tool

### Installation Steps

1. **Install Rust** (if not already installed):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Install maturin**:
   ```bash
   pip install maturin
   ```

3. **Build the Rust extension**:
   ```bash
   # Development build (unoptimized, faster compilation)
   maturin develop

   # Release build (optimized, slower compilation)
   maturin develop --release
   ```

4. **Verify installation**:
   ```python
   from heracless.rust_backend import is_rust_available
   print(f"Rust backend available: {is_rust_available()}")
   ```

## Development Workflow

### Project Structure

```
heracless/
├── src/                    # Rust source code
│   ├── lib.rs             # Main library & PyO3 bindings
│   ├── tree.rs            # Tree data structures
│   ├── codegen.rs         # Code generation (Rust & Python)
│   └── helper.rs          # Utility functions
├── heracless/             # Python package
│   ├── fight.py           # Main Python API
│   ├── rust_backend.py    # Python ↔ Rust bridge
│   └── utils/
│       └── cfg_tree.py    # Tree operations
├── Cargo.toml             # Rust dependencies
└── pyproject.toml         # Python package config (uses maturin)
```

### Making Changes

1. **Edit Rust code** in `src/` directory
2. **Rebuild** the extension:
   ```bash
   maturin develop
   ```
3. **Test** your changes:
   ```bash
   pytest tests/
   ```

### Running Rust Tests

```bash
# Run Rust unit tests
cargo test

# Run with verbose output
cargo test -- --nocapture

# Run specific test
cargo test test_load_config_tree
```

### Debugging

Enable Rust backtraces:
```bash
export RUST_BACKTRACE=1
python your_script.py
```

## PyO3 Bindings

The Rust backend exposes functions to Python via PyO3:

### Exposed Functions

```rust
#[pyfunction]
fn generate_python_stubs(config_path: String, frozen: bool) -> PyResult<String>
```
Generates Python dataclass type stubs from YAML config.

```rust
#[pyfunction]
fn parse_yaml_to_json(config_path: String) -> PyResult<String>
```
Parses YAML and returns JSON string for Python deserialization.

### Python Usage

```python
from heracless.rust_backend import generate_stubs_rust, parse_yaml_rust

# Generate type stubs
stubs = generate_stubs_rust(Path("config.yaml"), frozen=True)

# Parse YAML to dict
config_dict = parse_yaml_rust(Path("config.yaml"))
```

## Performance Comparison

Preliminary benchmarks (parsing 10KB YAML file, 1000 iterations):

| Implementation | Time      | Memory   |
|----------------|-----------|----------|
| Pure Python    | 2.4s      | 15 MB    |
| Rust Backend   | 0.3s      | 8 MB     |
| **Speedup**    | **8x**    | **47%**  |

## Fallback Behavior

If the Rust extension is not available:
- Heracless **automatically falls back** to the pure Python implementation
- A warning is issued on first import
- All functionality remains available (just slower)

```python
# This works even without Rust backend
from heracless import load_config
config = load_config("config.yaml", None, frozen=True)
```

## Troubleshooting

### Import Error: `heracless_core`

**Problem**: Python can't find the Rust extension.

**Solution**: Build the extension:
```bash
maturin develop
```

### Compilation Errors

**Problem**: Cargo build fails.

**Solutions**:
- Update Rust: `rustup update`
- Clean build: `cargo clean && cargo build`
- Check dependencies: `cargo update`

### Python API Changed

**Problem**: Existing Python code doesn't work.

**Note**: The Python API is unchanged! The Rust backend is transparent.

## Contributing to Rust Code

### Code Style

We use standard Rust conventions:
- Run `cargo fmt` before committing
- Run `cargo clippy` to check for issues
- Follow the existing code structure

### Adding New Features

1. Implement in Rust (`src/`)
2. Add PyO3 bindings in `src/lib.rs`
3. Create Python wrapper in `heracless/rust_backend.py`
4. Add tests in both Rust and Python
5. Update documentation

### Testing Checklist

- [ ] Rust tests pass: `cargo test`
- [ ] Python tests pass: `pytest`
- [ ] Type checking: `mypy heracless`
- [ ] Linting: `cargo clippy`
- [ ] Formatting: `cargo fmt --check`

## Release Process

1. **Update version** in `Cargo.toml` and `pyproject.toml`
2. **Build wheels** for multiple platforms:
   ```bash
   maturin build --release
   ```
3. **Test wheels** before publishing:
   ```bash
   pip install target/wheels/heracless-*.whl
   pytest
   ```
4. **Publish** to PyPI:
   ```bash
   maturin publish
   ```

## License

The Rust code is released under the same MIT License as the Python code.

## Questions?

- **Issues**: [GitHub Issues](https://github.com/felixscode/heracless/issues)
- **Discussions**: [GitHub Discussions](https://github.com/felixscode/heracless/discussions)
- **Email**: felix.schelling@protonmail.com
