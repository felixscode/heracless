//! Heracless: type-safe YAML configuration.
//!
//! This crate is the engine behind the `heracless` Python package. It parses a YAML
//! config (with PyYAML-compatible scalar resolution), infers a schema of named
//! classes from it, and generates code from that schema: Python type stubs for the
//! Python package, or serde structs for Rust users.
//!
//! ```
//! let doc = heracless::Document::from_str("server:\n  host: localhost\n  port: 8080\n")
//!     .unwrap()
//!     .expect("document is not empty");
//!
//! let stub = heracless::codegen::python::generate_stub(&doc.schema, true);
//! assert!(stub.contains("class Server:\n    host: str\n    port: int\n"));
//!
//! let rust = heracless::codegen::rust::generate(&doc.schema);
//! assert!(rust.contains("pub struct Server {"));
//! ```

pub mod codegen;
pub mod error;
pub mod naming;
pub mod schema;
pub mod value;
pub mod yaml;

#[cfg(feature = "python")]
mod python;

use std::path::Path;

pub use error::{Error, Result};
pub use schema::Schema;
pub use value::{Map, Value};

/// A loaded config: the parsed document and its inferred schema.
#[derive(Debug, Clone, PartialEq)]
pub struct Document {
    pub value: Map,
    pub schema: Schema,
}

impl Document {
    /// Build a document from a parsed value. `Null` (an empty file) yields `None`;
    /// anything other than a mapping at the top level is an error.
    pub fn from_value(value: Value) -> Result<Option<Document>> {
        match value {
            Value::Null => Ok(None),
            Value::Map(map) => Ok(Some(Document {
                schema: Schema::infer(&map),
                value: map,
            })),
            other => Err(Error::Config(format!(
                "the top level of a config file must be a mapping of keys to values, found a {}",
                other.kind_name()
            ))),
        }
    }

    /// Parse a YAML string. Returns `None` for an empty document.
    #[allow(clippy::should_implement_trait)] // returns Option, so FromStr doesn't fit
    pub fn from_str(source: &str) -> Result<Option<Document>> {
        Document::from_value(yaml::parse_str(source)?)
    }

    /// Load a YAML file. Returns `None` for an empty document.
    pub fn load(path: &Path) -> Result<Option<Document>> {
        Document::from_value(yaml::parse_file(path)?)
    }
}

/// Write `content` to `path` unless the file already holds exactly that content.
///
/// Leaving an unchanged file untouched keeps its mtime stable, so watchers, IDEs
/// and build tools don't react to every config load.
pub fn write_if_changed(path: &Path, content: &str) -> Result<()> {
    if std::fs::read(path).is_ok_and(|existing| existing == content.as_bytes()) {
        return Ok(());
    }
    std::fs::write(path, content).map_err(|e| Error::io("write", path, e))
}

/// Generate serde structs for the YAML config at `config_path` and write them to
/// `output_path`. Returns the generated code.
pub fn generate_rust_types(config_path: &Path, output_path: &Path) -> Result<String> {
    let doc = Document::load(config_path)?
        .ok_or_else(|| Error::Config(format!("{} is empty", config_path.display())))?;
    let code = codegen::rust::generate(&doc.schema);
    write_if_changed(output_path, &code)?;
    Ok(code)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write as _;

    #[test]
    fn load_and_generate() {
        let dir = tempfile::tempdir().unwrap();
        let config = dir.path().join("config.yaml");
        std::fs::File::create(&config)
            .unwrap()
            .write_all(b"app:\n  name: myapp\n  version: 1\n")
            .unwrap();
        let out = dir.path().join("config.rs");

        let code = generate_rust_types(&config, &out).unwrap();
        assert_eq!(std::fs::read_to_string(&out).unwrap(), code);
        assert!(code.contains("pub struct App {\n    pub name: String,\n    pub version: i64,\n}"));
    }

    #[test]
    fn errors() {
        assert!(matches!(
            Document::load(Path::new("/definitely/missing.yaml")),
            Err(Error::NotFound { .. })
        ));
        assert!(matches!(
            Document::from_str("- a\n- b\n"),
            Err(Error::Config(_))
        ));
        assert_eq!(Document::from_str("").unwrap(), None);
    }

    #[test]
    fn write_if_changed_keeps_identical_files() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("x.pyi");
        write_if_changed(&path, "a").unwrap();
        let before = std::fs::metadata(&path).unwrap().modified().unwrap();
        std::thread::sleep(std::time::Duration::from_millis(20));
        write_if_changed(&path, "a").unwrap();
        assert_eq!(
            std::fs::metadata(&path).unwrap().modified().unwrap(),
            before
        );
        write_if_changed(&path, "b").unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), "b");
    }
}
