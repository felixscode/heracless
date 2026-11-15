//! The in-memory representation of a parsed config document.

use std::fmt;

use indexmap::IndexMap;

/// A mapping with insertion order preserved (YAML key order drives field order).
pub type Map = IndexMap<String, Value>;

/// A config value. Mirrors what PyYAML's `full_load` produces for config-style documents.
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),
    /// An integer that doesn't fit in an `i64`, stored as a Python literal that
    /// `int(literal, 0)` accepts (e.g. `"-0x1f..."`, `"123..."`).
    BigInt(String),
    Float(f64),
    Str(String),
    Date(Date),
    DateTime(DateTime),
    Seq(Vec<Value>),
    Map(Map),
    /// A leaf owned by a language binding (e.g. an arbitrary Python object passed to
    /// `from_dict`). The core only carries the handle and a type hint.
    External {
        handle: usize,
        kind: ExternalKind,
    },
}

/// Type hint for [`Value::External`] leaves.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExternalKind {
    Date,
    DateTime,
    Any,
}

/// A calendar date (`YYYY-MM-DD`).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Date {
    pub year: u16,
    pub month: u8,
    pub day: u8,
}

/// A timestamp. `utc_offset` is in seconds; `None` means a naive (zone-less) datetime.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DateTime {
    pub date: Date,
    pub hour: u8,
    pub minute: u8,
    pub second: u8,
    pub microsecond: u32,
    pub utc_offset: Option<i32>,
}

impl fmt::Display for Date {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:04}-{:02}-{:02}", self.year, self.month, self.day)
    }
}

impl fmt::Display for DateTime {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} {:02}:{:02}:{:02}",
            self.date, self.hour, self.minute, self.second
        )?;
        if self.microsecond != 0 {
            write!(f, ".{:06}", self.microsecond)?;
        }
        if let Some(offset) = self.utc_offset {
            let sign = if offset < 0 { '-' } else { '+' };
            let offset = offset.unsigned_abs();
            write!(f, "{sign}{:02}:{:02}", offset / 3600, offset % 3600 / 60)?;
        }
        Ok(())
    }
}

impl Value {
    /// Short human-readable name of the value's kind, for error messages.
    pub fn kind_name(&self) -> &'static str {
        match self {
            Value::Null => "null",
            Value::Bool(_) => "bool",
            Value::Int(_) | Value::BigInt(_) => "int",
            Value::Float(_) => "float",
            Value::Str(_) => "str",
            Value::Date(_) => "date",
            Value::DateTime(_) => "datetime",
            Value::Seq(_) => "sequence",
            Value::Map(_) => "mapping",
            Value::External { .. } => "object",
        }
    }
}
