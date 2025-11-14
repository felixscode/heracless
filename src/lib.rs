//! Heracless - Type-safe YAML configuration management for Rust
//!
//! Transform your YAML config files into strongly-typed Rust structs with full type safety.
//!
//! # Examples
//!
//! ```no_run
//! use heracless::{load_config, generate_types};
//! use std::path::Path;
//!
//! // Generate type definitions from YAML
//! generate_types(
//!     Path::new("config.yaml"),
//!     Path::new("src/config.rs"),
//!     true
//! ).unwrap();
//! ```

pub mod codegen;
pub mod helper;
pub mod tree;

use std::path::Path;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum HeraclessError {
    #[error("YAML parsing error: {0}")]
    YamlError(#[from] serde_yaml::Error),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Invalid configuration: {0}")]
    ConfigError(String),
}

pub type Result<T> = std::result::Result<T, HeraclessError>;

/// Load a YAML configuration file and parse it into a tree structure
///
/// # Arguments
///
/// * `config_path` - Path to the YAML configuration file
///
/// # Returns
///
/// Returns a `Tree` structure representing the parsed configuration
///
/// # Errors
///
/// Returns an error if:
/// - The file cannot be read
/// - The YAML is malformed
/// - The root element is not a mapping
pub fn load_config_tree(config_path: &Path) -> Result<tree::Tree> {
    let content = std::fs::read_to_string(config_path)?;
    let value: serde_yaml::Value = serde_yaml::from_str(&content)?;

    tree::parse_tree(&value).map_err(|e| HeraclessError::ConfigError(e))
}

/// Generate Rust type definitions from a YAML configuration file
///
/// # Arguments
///
/// * `config_path` - Path to the YAML configuration file
/// * `output_path` - Path where the generated Rust code should be written
/// * `frozen` - Whether the generated structs should be immutable (adds Clone, PartialEq)
///
/// # Returns
///
/// Returns the generated code as a string, and writes it to the output file
///
/// # Errors
///
/// Returns an error if:
/// - The config file cannot be read or parsed
/// - The output file cannot be written
///
/// # Examples
///
/// ```no_run
/// use heracless::generate_types;
/// use std::path::Path;
///
/// generate_types(
///     Path::new("config.yaml"),
///     Path::new("src/config.rs"),
///     true
/// ).unwrap();
/// ```
pub fn generate_types(config_path: &Path, output_path: &Path, frozen: bool) -> Result<String> {
    let tree = load_config_tree(config_path)?;
    let code = codegen::generate_code(&tree, frozen);

    std::fs::write(output_path, &code)?;

    Ok(code)
}

/// Generate Rust type definitions and return as string without writing to file
///
/// # Arguments
///
/// * `config_path` - Path to the YAML configuration file
/// * `frozen` - Whether the generated structs should be immutable
///
/// # Returns
///
/// Returns the generated code as a string
pub fn generate_types_string(config_path: &Path, frozen: bool) -> Result<String> {
    let tree = load_config_tree(config_path)?;
    Ok(codegen::generate_code(&tree, frozen))
}

/// Main function that loads config and optionally generates type file
///
/// This is the equivalent of Python's `fight()` function
///
/// # Arguments
///
/// * `config_path` - Path to the YAML configuration file
/// * `output_path` - Optional path where generated code should be written
/// * `frozen` - Whether the generated structs should be immutable
///
/// # Returns
///
/// Returns the generated code as a string if successful
pub fn fight(config_path: &Path, output_path: Option<&Path>, frozen: bool) -> Result<String> {
    let tree = load_config_tree(config_path)?;
    let code = codegen::generate_code(&tree, frozen);

    if let Some(path) = output_path {
        std::fs::write(path, &code)?;
    }

    Ok(code)
}

// Python bindings using PyO3
use pyo3::prelude::*;
use pyo3::exceptions::PyException;

/// Convert HeraclessError to Python exception
impl std::convert::From<HeraclessError> for PyErr {
    fn from(err: HeraclessError) -> PyErr {
        PyException::new_err(err.to_string())
    }
}

/// Generate Python type stub code from YAML config
///
/// This generates Python dataclass definitions with type annotations
#[pyfunction]
fn generate_python_stubs(config_path: String, frozen: bool) -> PyResult<String> {
    let path = Path::new(&config_path);
    let tree = load_config_tree(path)?;
    let code = codegen::generate_python_code(&tree, frozen);
    Ok(code)
}

/// Parse YAML and return as JSON string for Python to deserialize
#[pyfunction]
fn parse_yaml_to_json(config_path: String) -> PyResult<String> {
    let path = Path::new(&config_path);
    let content = std::fs::read_to_string(path)
        .map_err(|e| PyException::new_err(format!("Failed to read file: {}", e)))?;
    let value: serde_yaml::Value = serde_yaml::from_str(&content)
        .map_err(|e| PyException::new_err(format!("Failed to parse YAML: {}", e)))?;
    let json = serde_json::to_string(&value)
        .map_err(|e| PyException::new_err(format!("Failed to convert to JSON: {}", e)))?;
    Ok(json)
}

/// Python module definition
#[pymodule]
fn heracless_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_python_stubs, m)?)?;
    m.add_function(wrap_pyfunction!(parse_yaml_to_json, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_load_config_tree() {
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "database:\n  host: localhost\n  port: 5432").unwrap();

        let tree = load_config_tree(temp_file.path()).unwrap();
        assert_eq!(tree.name, "Config");
        assert_eq!(tree.children.len(), 1);
    }

    #[test]
    fn test_generate_types_string() {
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(
            temp_file,
            "app:\n  name: myapp\n  version: 1\n  debug: true"
        )
        .unwrap();

        let code = generate_types_string(temp_file.path(), true).unwrap();
        assert!(code.contains("pub struct App"));
        assert!(code.contains("pub struct Config"));
        assert!(code.contains("pub name: String"));
    }

    #[test]
    fn test_fight() {
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "test:\n  value: 42").unwrap();

        let code = fight(temp_file.path(), None, true).unwrap();
        assert!(code.contains("pub struct Test"));
        assert!(code.contains("pub struct Config"));
    }
}
