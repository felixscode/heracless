//! Error type shared by every stage of the pipeline.

use std::path::PathBuf;

use thiserror::Error;

/// Everything that can go wrong while loading a config or generating types.
#[derive(Debug, Error)]
pub enum Error {
    /// The config file (or the directory it should live in) does not exist.
    #[error("config file not found: {}", path.display())]
    NotFound { path: PathBuf },

    /// Any other I/O failure while reading the config or writing generated code.
    #[error("could not {action} {}: {source}", path.display())]
    Io {
        action: &'static str,
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },

    /// The document is not valid YAML, or uses YAML features heracless can't represent.
    #[error("{message} (line {line}, column {column})")]
    Yaml {
        message: String,
        line: usize,
        column: usize,
    },

    /// The YAML is valid but doesn't describe a usable config (e.g. the root is a list).
    #[error("{0}")]
    Config(String),
}

impl Error {
    pub(crate) fn io(
        action: &'static str,
        path: impl Into<PathBuf>,
        source: std::io::Error,
    ) -> Self {
        let path = path.into();
        if source.kind() == std::io::ErrorKind::NotFound {
            Error::NotFound { path }
        } else {
            Error::Io {
                action,
                path,
                source,
            }
        }
    }
}

pub type Result<T, E = Error> = std::result::Result<T, E>;
