//! YAML loading.
//!
//! Scalars are resolved the way PyYAML's `full_load` resolves them (YAML 1.1 rules),
//! so configs keep the exact types they had when heracless was built on PyYAML:
//! `yes`/`on` are booleans, `2001-01-23` is a date, `0o17`-style octal is spelled
//! `017`, `1e3` (no dot) stays a string, merge keys (`<<`) are honoured, and so on.

use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use regex::Regex;
use yaml_rust2::parser::{Event, Parser, Tag};
use yaml_rust2::scanner::{Marker, ScanError, TScalarStyle};

use crate::error::{Error, Result};
use crate::value::{Date, DateTime, Map, Value};

/// Maximum nesting depth of collections. Real configs are nowhere near this; the
/// limit keeps hostile input from exhausting the stack further down the pipeline.
pub const MAX_DEPTH: usize = 128;

/// Maximum number of nodes that aliases may copy in total. Aliases are expanded
/// into copies, so without a cap a few lines of nested aliases ("billion laughs")
/// could expand to billions of nodes.
pub const MAX_ALIAS_NODES: usize = 1_000_000;

const CORE_TAG: &str = "tag:yaml.org,2002:";

// The implicit resolvers from PyYAML's `resolver.py`, written without verbose mode.
static BOOL_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(?:yes|Yes|YES|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)$")
        .unwrap()
});
static INT_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^(?:[-+]?0b[0-1_]+|[-+]?0[0-7_]+|[-+]?(?:0|[1-9][0-9_]*)|[-+]?0x[0-9a-fA-F_]+|[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$",
    )
    .unwrap()
});
static FLOAT_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?|\.[0-9][0-9_]*(?:[eE][-+][0-9]+)?|[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$",
    )
    .unwrap()
});
static NULL_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^(?:~|null|Null|NULL|)$").unwrap());
static TIMESTAMP_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^(?:[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt]|[ \t]+)[0-9]{1,2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]*)?(?:[ \t]*(?:Z|[-+][0-9]{1,2}(?::[0-9]{2})?))?)$",
    )
    .unwrap()
});
static TIMESTAMP_PARTS_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})(?:(?:[Tt]|[ \t]+)(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})(?:\.(?P<fraction>[0-9]*))?(?:[ \t]*(?P<tz>Z|(?P<tz_sign>[-+])(?P<tz_hour>[0-9]{1,2})(?::(?P<tz_minute>[0-9]{2}))?))?)?$",
    )
    .unwrap()
});

/// Read and parse a YAML file. An empty document yields [`Value::Null`].
pub fn parse_file(path: &Path) -> Result<Value> {
    let source = std::fs::read_to_string(path).map_err(|e| Error::io("read", path, e))?;
    parse_str(&source)
}

/// Parse a YAML document. An empty document yields [`Value::Null`].
pub fn parse_str(source: &str) -> Result<Value> {
    let source = source.strip_prefix('\u{feff}').unwrap_or(source);
    let mut parser = Parser::new_from_str(source);
    let mut builder = Builder::default();
    let mut documents = 0;

    loop {
        let (event, mark) = parser.next_token().map_err(scan_error)?;
        match event {
            Event::Nothing | Event::StreamStart | Event::DocumentEnd => {}
            Event::StreamEnd => break,
            Event::DocumentStart => {
                documents += 1;
                if documents > 1 {
                    return Err(yaml_error(
                        "expected a single document, but the file contains several (separated by `---`)",
                        mark,
                    ));
                }
            }
            Event::Alias(id) => {
                let value = builder.resolve_alias(id, mark)?;
                builder.push(value, 0, mark)?;
            }
            Event::Scalar(text, style, anchor, tag) => {
                if builder.expects_key()
                    && style == TScalarStyle::Plain
                    && tag.is_none()
                    && text == "<<"
                {
                    builder.set_merge_key();
                    continue;
                }
                let value = resolve_scalar(text, style, tag.as_ref())
                    .map_err(|msg| yaml_error(msg, mark))?;
                builder.push(value, anchor, mark)?;
            }
            Event::SequenceStart(anchor, tag) => {
                check_collection_tag(tag.as_ref(), Collection::Seq)
                    .map_err(|msg| yaml_error(msg, mark))?;
                builder.open(
                    Frame::Seq {
                        anchor,
                        items: Vec::new(),
                    },
                    mark,
                )?;
            }
            Event::MappingStart(anchor, tag) => {
                let is_set = check_collection_tag(tag.as_ref(), Collection::Map)
                    .map_err(|msg| yaml_error(msg, mark))?;
                builder.open(
                    Frame::Map {
                        anchor,
                        is_set,
                        pending_key: None,
                        pairs: Vec::new(),
                    },
                    mark,
                )?;
            }
            Event::SequenceEnd => match builder.stack.pop() {
                Some(Frame::Seq { anchor, items }) => {
                    builder.push(Value::Seq(items), anchor, mark)?
                }
                _ => return Err(yaml_error("unbalanced sequence end", mark)),
            },
            Event::MappingEnd => match builder.stack.pop() {
                Some(Frame::Map {
                    anchor,
                    is_set,
                    pairs,
                    ..
                }) => {
                    let value =
                        build_mapping(pairs, is_set).map_err(|msg| yaml_error(msg, mark))?;
                    builder.push(value, anchor, mark)?;
                }
                _ => return Err(yaml_error("unbalanced mapping end", mark)),
            },
        }
    }
    Ok(builder.root.unwrap_or(Value::Null))
}

fn scan_error(err: ScanError) -> Error {
    Error::Yaml {
        message: err.info().to_string(),
        line: err.marker().line(),
        column: err.marker().col() + 1,
    }
}

fn yaml_error(message: impl Into<String>, mark: Marker) -> Error {
    Error::Yaml {
        message: message.into(),
        line: mark.line(),
        column: mark.col() + 1,
    }
}

enum Key {
    Merge,
    Value(Value),
}

enum Frame {
    Seq {
        anchor: usize,
        items: Vec<Value>,
    },
    Map {
        anchor: usize,
        is_set: bool,
        pending_key: Option<Key>,
        pairs: Vec<(Key, Value)>,
    },
}

struct Anchor {
    value: Value,
    nodes: usize,
    depth: usize,
}

#[derive(Default)]
struct Builder {
    stack: Vec<Frame>,
    anchors: HashMap<usize, Anchor>,
    alias_nodes: usize,
    root: Option<Value>,
}

/// Number of nodes in `value`, and how deeply its collections nest.
fn measure(value: &Value) -> (usize, usize) {
    let children: Box<dyn Iterator<Item = &Value>> = match value {
        Value::Seq(items) => Box::new(items.iter()),
        Value::Map(map) => Box::new(map.values()),
        _ => return (1, 0),
    };
    children.fold((1, 1), |(nodes, depth), child| {
        let (n, d) = measure(child);
        (nodes + n, depth.max(d + 1))
    })
}

impl Builder {
    fn expects_key(&self) -> bool {
        matches!(
            self.stack.last(),
            Some(Frame::Map {
                pending_key: None,
                ..
            })
        )
    }

    fn set_merge_key(&mut self) {
        if let Some(Frame::Map { pending_key, .. }) = self.stack.last_mut() {
            *pending_key = Some(Key::Merge);
        }
    }

    fn open(&mut self, frame: Frame, mark: Marker) -> Result<()> {
        if self.stack.len() >= MAX_DEPTH {
            return Err(yaml_error(
                format!("document is nested deeper than {MAX_DEPTH} levels"),
                mark,
            ));
        }
        self.stack.push(frame);
        Ok(())
    }

    /// A copy of the value anchored as `id`, within the depth and expansion limits.
    fn resolve_alias(&mut self, id: usize, mark: Marker) -> Result<Value> {
        let anchor = self
            .anchors
            .get(&id)
            .ok_or_else(|| yaml_error("alias refers to an unknown or unfinished anchor", mark))?;
        if self.stack.len() + anchor.depth > MAX_DEPTH {
            return Err(yaml_error(
                format!("document is nested deeper than {MAX_DEPTH} levels"),
                mark,
            ));
        }
        self.alias_nodes += anchor.nodes;
        if self.alias_nodes > MAX_ALIAS_NODES {
            return Err(yaml_error(
                format!("aliases expand to more than {MAX_ALIAS_NODES} nodes"),
                mark,
            ));
        }
        Ok(anchor.value.clone())
    }

    /// Attach a finished node to its parent (or make it the document root).
    fn push(&mut self, value: Value, anchor: usize, mark: Marker) -> Result<()> {
        if anchor != 0 {
            let (nodes, depth) = measure(&value);
            let anchored = Anchor {
                value: value.clone(),
                nodes,
                depth,
            };
            self.anchors.insert(anchor, anchored);
        }
        match self.stack.last_mut() {
            None if self.root.is_none() => self.root = Some(value),
            None => {
                return Err(yaml_error(
                    "unexpected content after the document root",
                    mark,
                ))
            }
            Some(Frame::Seq { items, .. }) => items.push(value),
            Some(Frame::Map {
                pending_key, pairs, ..
            }) => match pending_key.take() {
                None => *pending_key = Some(Key::Value(value)),
                Some(key) => pairs.push((key, value)),
            },
        }
        Ok(())
    }
}

/// Build a mapping, applying merge keys exactly like PyYAML's `flatten_mapping`:
/// explicit keys beat merged ones, and in `<<: [*a, *b]` the earlier source wins.
fn build_mapping(pairs: Vec<(Key, Value)>, is_set: bool) -> Result<Value, String> {
    let mut merged: Vec<(String, Value)> = Vec::new();
    let mut explicit: Vec<(String, Value)> = Vec::with_capacity(pairs.len());

    for (key, value) in pairs {
        match key {
            Key::Value(key) => explicit.push((key_to_string(key)?, value)),
            Key::Merge => match value {
                Value::Map(map) => merged.extend(map),
                Value::Seq(items) => {
                    let mut sources = Vec::with_capacity(items.len());
                    for item in items {
                        match item {
                            Value::Map(map) => sources.push(map),
                            other => {
                                return Err(format!(
                                    "merge key `<<` expects mappings, but the list contains a {}",
                                    other.kind_name()
                                ))
                            }
                        }
                    }
                    for map in sources.into_iter().rev() {
                        merged.extend(map);
                    }
                }
                other => {
                    return Err(format!(
                        "merge key `<<` expects a mapping or a list of mappings, found a {}",
                        other.kind_name()
                    ))
                }
            },
        }
    }

    let mut map = Map::with_capacity(merged.len() + explicit.len());
    for (key, value) in merged.into_iter().chain(explicit) {
        map.insert(key, value);
    }
    if is_set {
        return Ok(Value::Seq(map.into_keys().map(Value::Str).collect()));
    }
    Ok(Value::Map(map))
}

/// Mapping keys become strings, spelled the way Python's `str()` would spell them.
fn key_to_string(key: Value) -> Result<String, String> {
    Ok(match key {
        Value::Str(s) => s,
        Value::Int(i) => i.to_string(),
        Value::BigInt(literal) => literal,
        Value::Bool(true) => "True".into(),
        Value::Bool(false) => "False".into(),
        Value::Null => "None".into(),
        Value::Float(f) => python_float_repr(f),
        Value::Date(d) => d.to_string(),
        Value::DateTime(dt) => dt.to_string(),
        other => {
            return Err(format!(
                "mapping keys must be scalars, found a {}",
                other.kind_name()
            ))
        }
    })
}

fn python_float_repr(f: f64) -> String {
    if f.is_nan() {
        "nan".into()
    } else if f.is_infinite() {
        if f > 0.0 { "inf" } else { "-inf" }.into()
    } else {
        format!("{f:?}")
    }
}

#[derive(Clone, Copy, PartialEq)]
enum Collection {
    Seq,
    Map,
}

/// Validate a collection tag. Returns `true` for `!!set` mappings.
fn check_collection_tag(tag: Option<&Tag>, kind: Collection) -> Result<bool, String> {
    let Some(tag) = tag else { return Ok(false) };
    let name = tag_name(tag);
    let ok = match kind {
        Collection::Seq => matches!(
            name.as_str(),
            "!" | "seq" | "omap" | "pairs" | "python/list" | "python/tuple"
        ),
        Collection::Map => {
            if name == "set" {
                return Ok(true);
            }
            matches!(name.as_str(), "!" | "map" | "python/dict")
        }
    };
    if ok {
        Ok(false)
    } else {
        Err(format!("unsupported tag `{}{}`", tag.handle, tag.suffix))
    }
}

/// `!!str` -> `str`, `!custom` -> `!custom`; core tags lose their prefix.
fn tag_name(tag: &Tag) -> String {
    if tag.handle == CORE_TAG {
        tag.suffix.clone()
    } else if tag.handle == "!" && tag.suffix.is_empty() {
        "!".into()
    } else {
        format!("{}{}", tag.handle, tag.suffix)
    }
}

fn resolve_scalar(text: String, style: TScalarStyle, tag: Option<&Tag>) -> Result<Value, String> {
    let Some(tag) = tag else {
        return Ok(if style == TScalarStyle::Plain {
            resolve_plain(text)?
        } else {
            Value::Str(text)
        });
    };
    let invalid = |what: &str| format!("cannot interpret {text:?} as {what}");
    match tag_name(tag).as_str() {
        "!" | "str" | "python/str" | "python/unicode" => Ok(Value::Str(text)),
        "int" | "python/int" => construct_int(&text).ok_or_else(|| invalid("an integer")),
        "float" | "python/float" => construct_float(&text)
            .map(Value::Float)
            .ok_or_else(|| invalid("a float")),
        "bool" | "python/bool" => match text.to_ascii_lowercase().as_str() {
            "yes" | "true" | "on" => Ok(Value::Bool(true)),
            "no" | "false" | "off" => Ok(Value::Bool(false)),
            _ => Err(invalid("a boolean")),
        },
        "null" | "python/none" => Ok(Value::Null),
        "timestamp" => construct_timestamp(&text),
        _ => Err(format!("unsupported tag `{}{}`", tag.handle, tag.suffix)),
    }
}

fn resolve_plain(text: String) -> Result<Value, String> {
    if NULL_RE.is_match(&text) {
        return Ok(Value::Null);
    }
    if BOOL_RE.is_match(&text) {
        return Ok(Value::Bool(matches!(
            text.to_ascii_lowercase().as_str(),
            "yes" | "true" | "on"
        )));
    }
    if INT_RE.is_match(&text) {
        return construct_int(&text).ok_or_else(|| format!("invalid integer {text:?}"));
    }
    if FLOAT_RE.is_match(&text) {
        return construct_float(&text)
            .map(Value::Float)
            .ok_or_else(|| format!("invalid float {text:?}"));
    }
    if TIMESTAMP_RE.is_match(&text) {
        return construct_timestamp(&text);
    }
    Ok(Value::Str(text))
}

fn split_sign(text: &str) -> (bool, &str) {
    match text.as_bytes().first() {
        Some(b'-') => (true, &text[1..]),
        Some(b'+') => (false, &text[1..]),
        _ => (false, text),
    }
}

/// PyYAML's `construct_yaml_int`: binary, octal (`017`), hex, sexagesimal and decimal.
fn construct_int(text: &str) -> Option<Value> {
    let cleaned: String = text.chars().filter(|&c| c != '_').collect();
    let (negative, body) = split_sign(&cleaned);
    let sign = if negative { "-" } else { "" };

    if body.contains(':') {
        let mut total: i128 = 0;
        for part in body.split(':') {
            total = total
                .checked_mul(60)?
                .checked_add(part.parse::<i128>().ok()?)?;
        }
        let total = if negative { -total } else { total };
        return Some(
            i64::try_from(total).map_or_else(|_| Value::BigInt(total.to_string()), Value::Int),
        );
    }

    let (radix, digits, prefix) = if let Some(d) = body.strip_prefix("0b") {
        (2, d, "0b")
    } else if let Some(d) = body.strip_prefix("0x") {
        (16, d, "0x")
    } else if body.len() > 1 && body.starts_with('0') {
        (8, &body[1..], "0o")
    } else {
        (10, body, "")
    };
    if digits.is_empty() {
        return None;
    }
    match u64::from_str_radix(digits, radix) {
        Ok(magnitude) => {
            let signed = if negative {
                -(magnitude as i128)
            } else {
                magnitude as i128
            };
            Some(
                i64::try_from(signed)
                    .map_or_else(|_| Value::BigInt(signed.to_string()), Value::Int),
            )
        }
        Err(e) if *e.kind() == std::num::IntErrorKind::PosOverflow => {
            Some(Value::BigInt(format!("{sign}{prefix}{digits}")))
        }
        Err(_) => None,
    }
}

/// PyYAML's `construct_yaml_float`, including `.inf`, `.nan` and sexagesimal floats.
fn construct_float(text: &str) -> Option<f64> {
    let cleaned: String = text
        .chars()
        .filter(|&c| c != '_')
        .collect::<String>()
        .to_ascii_lowercase();
    let (negative, body) = split_sign(&cleaned);
    let sign = if negative { -1.0 } else { 1.0 };

    let magnitude = if body == ".inf" {
        f64::INFINITY
    } else if body == ".nan" {
        return Some(f64::NAN);
    } else if body.contains(':') {
        let mut total = 0.0;
        for part in body.split(':') {
            total = total * 60.0 + parse_python_float(part)?;
        }
        total
    } else {
        parse_python_float(body)?
    };
    Some(sign * magnitude)
}

/// Parse a float the way Python's `float()` does for YAML-style input (`1.`, `.5`, `1.e+5`).
fn parse_python_float(text: &str) -> Option<f64> {
    if let Ok(f) = text.parse::<f64>() {
        return Some(f);
    }
    let mut normalized = text.replace(".e", ".0e");
    if normalized.starts_with('.') {
        normalized.insert(0, '0');
    }
    if normalized.ends_with('.') {
        normalized.push('0');
    }
    normalized.parse::<f64>().ok()
}

/// PyYAML's `construct_yaml_timestamp`: a date, or a datetime with optional UTC offset.
fn construct_timestamp(text: &str) -> Result<Value, String> {
    let invalid = || format!("invalid timestamp {text:?}");
    let caps = TIMESTAMP_PARTS_RE.captures(text).ok_or_else(invalid)?;
    let num = |name: &str| {
        caps.name(name)
            .map(|m| m.as_str().parse::<u32>().unwrap_or(u32::MAX))
    };

    let year = num("year").unwrap_or(0);
    let month = num("month").unwrap_or(0);
    let day = num("day").unwrap_or(0);
    if !(1..=9999).contains(&year)
        || !(1..=12).contains(&month)
        || day == 0
        || day > days_in_month(year, month)
    {
        return Err(invalid());
    }
    let date = Date {
        year: year as u16,
        month: month as u8,
        day: day as u8,
    };

    let Some(hour) = num("hour") else {
        return Ok(Value::Date(date));
    };
    let (minute, second) = (num("minute").unwrap_or(0), num("second").unwrap_or(0));
    if hour > 23 || minute > 59 || second > 59 {
        return Err(invalid());
    }

    let microsecond = caps.name("fraction").map_or(0, |m| {
        let digits: String = m
            .as_str()
            .chars()
            .chain(std::iter::repeat('0'))
            .take(6)
            .collect();
        digits.parse().unwrap_or(0)
    });

    let utc_offset = match (caps.name("tz"), caps.name("tz_sign")) {
        (None, _) => None,
        (Some(_), None) => Some(0), // `Z`
        (Some(_), Some(sign)) => {
            let offset =
                (num("tz_hour").unwrap_or(0) * 3600 + num("tz_minute").unwrap_or(0) * 60) as i32;
            if offset >= 24 * 3600 {
                return Err(invalid());
            }
            Some(if sign.as_str() == "-" {
                -offset
            } else {
                offset
            })
        }
    };

    Ok(Value::DateTime(DateTime {
        date,
        hour: hour as u8,
        minute: minute as u8,
        second: second as u8,
        microsecond,
        utc_offset,
    }))
}

fn days_in_month(year: u32, month: u32) -> u32 {
    match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if (year % 4 == 0 && year % 100 != 0) || year % 400 == 0 => 29,
        2 => 28,
        _ => 0,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    fn scalar(text: &str) -> Value {
        match parse_str(&format!("v: {text}")).unwrap() {
            Value::Map(mut m) => m.shift_remove("v").unwrap(),
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn resolves_yaml_1_1_scalars_like_pyyaml() {
        assert_eq!(scalar("yes"), Value::Bool(true));
        assert_eq!(scalar("Off"), Value::Bool(false));
        assert_eq!(scalar("~"), Value::Null);
        assert_eq!(scalar(""), Value::Null);
        assert_eq!(scalar("42"), Value::Int(42));
        assert_eq!(scalar("-1_000"), Value::Int(-1000));
        assert_eq!(scalar("017"), Value::Int(15));
        assert_eq!(scalar("0x1F"), Value::Int(31));
        assert_eq!(scalar("0b101"), Value::Int(5));
        assert_eq!(scalar("1:30"), Value::Int(90));
        assert_eq!(scalar("1.5"), Value::Float(1.5));
        assert_eq!(scalar("1."), Value::Float(1.0));
        assert_eq!(scalar("1.e+3"), Value::Float(1000.0));
        assert_eq!(scalar("-.inf"), Value::Float(f64::NEG_INFINITY));
        assert_eq!(scalar("1e3"), Value::Str("1e3".into()));
        assert_eq!(scalar("'42'"), Value::Str("42".into()));
        assert_eq!(scalar("1.0.0"), Value::Str("1.0.0".into()));
        assert_eq!(
            scalar("99999999999999999999"),
            Value::BigInt("99999999999999999999".into())
        );
        assert_eq!(scalar("-0x8000000000000000"), Value::Int(i64::MIN));
    }

    #[test]
    fn resolves_timestamps() {
        assert_eq!(
            scalar("2001-01-23"),
            Value::Date(Date {
                year: 2001,
                month: 1,
                day: 23
            })
        );
        let Value::DateTime(dt) = scalar("2001-12-14t21:59:43.10-05:00") else {
            panic!()
        };
        assert_eq!(
            (dt.hour, dt.microsecond, dt.utc_offset),
            (21, 100_000, Some(-5 * 3600))
        );
        let Value::DateTime(dt) = scalar("2001-12-14 21:59:43Z") else {
            panic!()
        };
        assert_eq!(dt.utc_offset, Some(0));
        assert!(parse_str("v: 2001-02-30").is_err());
        assert_eq!(scalar("'2001-01-23'"), Value::Str("2001-01-23".into()));
    }

    #[test]
    fn explicit_tags() {
        assert_eq!(scalar("!!str 42"), Value::Str("42".into()));
        assert_eq!(scalar("!!int '42'"), Value::Int(42));
        assert_eq!(scalar("!!float 1"), Value::Float(1.0));
        assert!(parse_str("v: !!binary aGk=").is_err());
        assert!(parse_str("v: !custom x").is_err());
    }

    #[test]
    fn merge_keys_follow_pyyaml_precedence() {
        let doc = "a: &a {x: 1, y: 1}\nb: &b {y: 2, z: 2}\nc:\n  <<: [*a, *b]\n  z: 3\n";
        let Value::Map(root) = parse_str(doc).unwrap() else {
            panic!()
        };
        let Value::Map(c) = &root["c"] else { panic!() };
        let entries: Vec<_> = c.iter().map(|(k, v)| (k.as_str(), v.clone())).collect();
        assert_eq!(
            entries,
            [
                ("y", Value::Int(1)),
                ("z", Value::Int(3)),
                ("x", Value::Int(1))
            ]
        );
    }

    #[test]
    fn anchors_and_aliases() {
        let Value::Map(root) = parse_str("a: &x {k: v}\nb: *x\n").unwrap() else {
            panic!()
        };
        assert_eq!(root["a"], root["b"]);
        assert!(parse_str("a: *nope").is_err());
    }

    #[test]
    fn empty_documents_are_null() {
        assert_eq!(parse_str("").unwrap(), Value::Null);
        assert_eq!(parse_str("# only a comment\n").unwrap(), Value::Null);
        assert_eq!(parse_str("~").unwrap(), Value::Null);
    }

    #[test]
    fn rejects_multiple_documents_and_bad_syntax() {
        assert!(matches!(
            parse_str("a: 1\n---\nb: 2\n"),
            Err(Error::Yaml { line: 2, .. })
        ));
        assert!(matches!(parse_str("a: [1\n"), Err(Error::Yaml { .. })));
    }

    #[test]
    fn scalar_keys_are_stringified() {
        let Value::Map(root) = parse_str("1: a\ntrue: b\n~: c\n").unwrap() else {
            panic!()
        };
        assert_eq!(root.keys().collect::<Vec<_>>(), ["1", "True", "None"]);
        assert!(parse_str("[1]: a").is_err());
    }

    #[test]
    fn alias_bombs_are_rejected() {
        let mut doc = String::from("a0: &a0 [x, x, x, x, x, x, x, x, x, x]\n");
        for i in 1..10 {
            let prev = format!("*a{}", i - 1);
            doc += &format!("a{i}: &a{i} [{}]\n", [prev.as_str(); 10].join(", "));
        }
        let err = parse_str(&doc).unwrap_err().to_string();
        assert!(err.contains("aliases expand"), "{err}");
    }

    #[test]
    fn aliases_cannot_exceed_depth_limit() {
        let half = MAX_DEPTH / 2 + 1;
        let deep = "[".repeat(half) + &"]".repeat(half);
        let doc = format!(
            "a: &a {deep}\nb: &b [*a]\nc: {}*b{}\n",
            "[".repeat(half),
            "]".repeat(half)
        );
        let err = parse_str(&doc).unwrap_err().to_string();
        assert!(err.contains("nested deeper"), "{err}");
    }

    #[test]
    fn depth_limit() {
        let deep = "[".repeat(MAX_DEPTH + 1) + &"]".repeat(MAX_DEPTH + 1);
        assert!(parse_str(&deep).is_err());
    }
}
