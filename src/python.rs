//! Python bindings (`heracless._core`).
//!
//! Parsing, inference and stub generation run without holding the GIL; only
//! building the resulting Python objects needs it.

use std::path::PathBuf;

use pyo3::exceptions::{PyOSError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{
    PyBool, PyDict, PyFloat, PyFrozenSet, PyInt, PyList, PyMapping, PySet, PyString, PyTuple,
    PyType,
};

use crate::codegen::python::{generate_stub as render_stub, render_type};
use crate::error::Error;
use crate::schema::{ClassId, Schema, Ty};
use crate::value::{ExternalKind, Map, Value};
use crate::yaml::MAX_DEPTH;
use crate::{write_if_changed, Document};

const EXCEPTIONS_MODULE: &str = "heracless.utils.exceptions";

/// Raise one of heracless' Python exception classes (falling back to `fallback`
/// if the module can't be imported, which only happens in a broken install).
fn heracless_exception(
    py: Python<'_>,
    class: &str,
    message: String,
    fallback: fn(String) -> PyErr,
) -> PyErr {
    match py
        .import(EXCEPTIONS_MODULE)
        .and_then(|m| m.getattr(class))
        .and_then(|c| c.cast_into::<PyType>().map_err(PyErr::from))
    {
        Ok(class) => PyErr::from_type(class, (message,)),
        Err(_) => fallback(message),
    }
}

fn to_py_err(py: Python<'_>, err: Error) -> PyErr {
    match err {
        Error::NotFound { path } => {
            heracless_exception(py, "DirectoryError", path.display().to_string(), |m| {
                pyo3::exceptions::PyFileNotFoundError::new_err(m)
            })
        }
        Error::Io {
            ref source,
            ref path,
            ..
        } => match source.raw_os_error() {
            // OSError(errno, strerror, filename) picks the matching subclass
            // (PermissionError, IsADirectoryError, ...).
            Some(code) => {
                let message = source.to_string();
                let strerror = message
                    .split(" (os error")
                    .next()
                    .unwrap_or(&message)
                    .to_string();
                PyOSError::new_err((code, strerror, path.display().to_string()))
            }
            None => PyOSError::new_err(err.to_string()),
        },
        Error::Yaml { .. } => heracless_exception(
            py,
            "YamlSyntaxError",
            err.to_string(),
            PyValueError::new_err,
        ),
        Error::Config(message) => {
            heracless_exception(py, "ConfigError", message, PyValueError::new_err)
        }
    }
}

/// Converts leaves and schema-less values into plain Python objects.
struct Leaves<'py, 'a> {
    py: Python<'py>,
    datetime: Bound<'py, PyModule>,
    externals: &'a [Py<PyAny>],
}

impl<'py, 'a> Leaves<'py, 'a> {
    fn new(py: Python<'py>, externals: &'a [Py<PyAny>]) -> PyResult<Self> {
        Ok(Leaves {
            py,
            datetime: py.import("datetime")?,
            externals,
        })
    }

    /// Convert without a schema: mappings become dicts, sequences lists (like PyYAML).
    fn plain(&self, value: &Value) -> PyResult<Bound<'py, PyAny>> {
        match value {
            Value::Map(map) => {
                let dict = PyDict::new(self.py);
                for (key, value) in map {
                    dict.set_item(key, self.plain(value)?)?;
                }
                Ok(dict.into_any())
            }
            Value::Seq(items) => {
                let items = items
                    .iter()
                    .map(|v| self.plain(v))
                    .collect::<PyResult<Vec<_>>>()?;
                Ok(PyList::new(self.py, items)?.into_any())
            }
            _ => self.scalar(value),
        }
    }

    fn scalar(&self, value: &Value) -> PyResult<Bound<'py, PyAny>> {
        let py = self.py;
        Ok(match value {
            Value::Null => py.None().into_bound(py),
            Value::Bool(b) => PyBool::new(py, *b).to_owned().into_any(),
            Value::Int(i) => i.into_pyobject(py)?.into_any(),
            Value::BigInt(literal) => py.get_type::<PyInt>().call1((literal, 0))?,
            Value::Float(f) => PyFloat::new(py, *f).into_any(),
            Value::Str(s) => PyString::new(py, s).into_any(),
            Value::Date(d) => self
                .datetime
                .getattr("date")?
                .call1((d.year, d.month, d.day))?,
            Value::DateTime(dt) => {
                let tzinfo = match dt.utc_offset {
                    None => py.None().into_bound(py),
                    Some(0) => self.datetime.getattr("timezone")?.getattr("utc")?,
                    Some(seconds) => {
                        let kwargs = PyDict::new(py);
                        kwargs.set_item("seconds", seconds)?;
                        let delta = self
                            .datetime
                            .getattr("timedelta")?
                            .call((), Some(&kwargs))?;
                        self.datetime.getattr("timezone")?.call1((delta,))?
                    }
                };
                let kwargs = PyDict::new(py);
                kwargs.set_item("tzinfo", tzinfo)?;
                let d = dt.date;
                self.datetime.getattr("datetime")?.call(
                    (
                        d.year,
                        d.month,
                        d.day,
                        dt.hour,
                        dt.minute,
                        dt.second,
                        dt.microsecond,
                    ),
                    Some(&kwargs),
                )?
            }
            Value::External { handle, .. } => self.externals[*handle].bind(py).clone(),
            Value::Map(_) | Value::Seq(_) => {
                unreachable!("collections are handled by plain() or ObjectBuilder::convert()")
            }
        })
    }
}

/// Builds config objects (dataclass instances and tuples) from values and their schema.
struct ObjectBuilder<'py, 'a> {
    leaves: Leaves<'py, 'a>,
    schema: &'a Schema,
    frozen: bool,
    classes: Vec<Option<Bound<'py, PyAny>>>,
}

impl<'py, 'a> ObjectBuilder<'py, 'a> {
    fn new(
        py: Python<'py>,
        schema: &'a Schema,
        frozen: bool,
        externals: &'a [Py<PyAny>],
    ) -> PyResult<Self> {
        Ok(ObjectBuilder {
            leaves: Leaves::new(py, externals)?,
            schema,
            frozen,
            classes: vec![None; schema.len()],
        })
    }

    /// The dataclass for `id`, created on first use.
    fn class(&mut self, id: ClassId) -> PyResult<Bound<'py, PyAny>> {
        if let Some(class) = &self.classes[id] {
            return Ok(class.clone());
        }
        let py = self.leaves.py;
        let def = self.schema.class(id);
        let fields: Vec<(String, String)> = def
            .fields
            .iter()
            .map(|f| (f.name.clone(), render_type(self.schema, &f.ty)))
            .collect();
        let kwargs = PyDict::new(py);
        kwargs.set_item("frozen", self.frozen)?;
        let class = py
            .import("dataclasses")?
            .getattr("make_dataclass")?
            .call((def.name.as_str(), fields), Some(&kwargs))?;
        self.classes[id] = Some(class.clone());
        Ok(class)
    }

    fn instance(&mut self, id: ClassId, map: &Map) -> PyResult<Bound<'py, PyAny>> {
        let py = self.leaves.py;
        let class = self.class(id)?;
        let kwargs = PyDict::new(py);
        for field in &self.schema.class(id).fields {
            let value = match map.get(&field.key) {
                Some(value) => self.convert(value, &field.ty)?,
                None => py.None().into_bound(py),
            };
            kwargs.set_item(field.name.as_str(), value)?;
        }
        class.call((), Some(&kwargs))
    }

    fn root(&mut self, map: &Map) -> PyResult<Py<PyAny>> {
        Ok(self.instance(self.schema.root(), map)?.unbind())
    }

    /// Convert a value of (inferred) type `ty`.
    fn convert(&mut self, value: &Value, ty: &Ty) -> PyResult<Bound<'py, PyAny>> {
        match value {
            Value::Map(map) => match ty.class_id() {
                Some(id) => self.instance(id, map),
                None => self.leaves.plain(value),
            },
            Value::Seq(items) => {
                let element = ty.element().cloned().unwrap_or(Ty::Any);
                let items = items
                    .iter()
                    .map(|item| self.convert(item, &element))
                    .collect::<PyResult<Vec<_>>>()?;
                Ok(PyTuple::new(self.leaves.py, items)?.into_any())
            }
            _ => self.leaves.scalar(value),
        }
    }
}

/// Convert a Python object into a [`Value`]. Leaves the core can't represent are
/// kept as [`Value::External`] handles into `externals`.
fn from_py(
    obj: &Bound<'_, PyAny>,
    externals: &mut Vec<Py<PyAny>>,
    depth: usize,
) -> PyResult<Value> {
    if depth > MAX_DEPTH {
        return Err(PyValueError::new_err(format!(
            "config is nested deeper than {MAX_DEPTH} levels (or contains a reference cycle)"
        )));
    }
    let py = obj.py();
    if obj.is_none() {
        return Ok(Value::Null);
    }
    if let Ok(b) = obj.cast::<PyBool>() {
        return Ok(Value::Bool(b.is_true()));
    }
    if obj.is_instance_of::<PyInt>() {
        return Ok(match obj.extract::<i64>() {
            Ok(i) => Value::Int(i),
            // Normalise int subclasses (e.g. IntEnum) to their plain decimal spelling.
            Err(_) => Value::BigInt(py.get_type::<PyInt>().call1((obj,))?.str()?.to_string()),
        });
    }
    if obj.is_instance_of::<PyFloat>() {
        return Ok(Value::Float(obj.extract::<f64>()?));
    }
    if obj.is_instance_of::<PyString>() {
        return Ok(Value::Str(obj.extract::<String>()?));
    }
    if obj.is_instance_of::<PyDict>() || obj.is_instance_of::<PyMapping>() {
        let mapping = obj.cast::<PyMapping>()?;
        let mut map = Map::with_capacity(mapping.len()?);
        for item in mapping.items()?.iter() {
            let (key, value): (Bound<'_, PyAny>, Bound<'_, PyAny>) = item.extract()?;
            let key = match key.cast::<PyString>() {
                Ok(s) => s.to_string(),
                Err(_) => key.str()?.to_string(),
            };
            map.insert(key, from_py(&value, externals, depth + 1)?);
        }
        return Ok(Value::Map(map));
    }
    if obj.is_instance_of::<PyList>()
        || obj.is_instance_of::<PyTuple>()
        || obj.is_instance_of::<PySet>()
        || obj.is_instance_of::<PyFrozenSet>()
    {
        let items = obj
            .try_iter()?
            .map(|item| from_py(&item?, externals, depth + 1))
            .collect::<PyResult<Vec<_>>>()?;
        return Ok(Value::Seq(items));
    }

    let datetime = py.import("datetime")?;
    // `datetime` subclasses `date`, so test it first.
    let kind = if obj.is_instance(&datetime.getattr("datetime")?)? {
        ExternalKind::DateTime
    } else if obj.is_instance(&datetime.getattr("date")?)? {
        ExternalKind::Date
    } else {
        ExternalKind::Any
    };
    externals.push(obj.clone().unbind());
    Ok(Value::External {
        handle: externals.len() - 1,
        kind,
    })
}

/// Load a config file into a dataclass instance (``None`` for an empty file),
/// optionally writing a type stub for it to ``stub_path``.
#[pyfunction]
#[pyo3(signature = (path, frozen = true, stub_path = None))]
fn load_config(
    py: Python<'_>,
    path: PathBuf,
    frozen: bool,
    stub_path: Option<PathBuf>,
) -> PyResult<Py<PyAny>> {
    let doc = py
        .detach(|| -> crate::Result<Option<Document>> {
            let doc = Document::load(&path)?;
            if let (Some(doc), Some(stub_path)) = (&doc, &stub_path) {
                write_if_changed(stub_path, &render_stub(&doc.schema, frozen))?;
            }
            Ok(doc)
        })
        .map_err(|e| to_py_err(py, e))?;
    match doc {
        None => Ok(py.None()),
        Some(doc) => ObjectBuilder::new(py, &doc.schema, frozen, &[])?.root(&doc.value),
    }
}

/// Generate the type stub for a config file (``None`` for an empty file).
#[pyfunction]
#[pyo3(signature = (path, frozen = true))]
fn generate_stub(py: Python<'_>, path: PathBuf, frozen: bool) -> PyResult<Option<String>> {
    py.detach(|| Ok(Document::load(&path)?.map(|doc| render_stub(&doc.schema, frozen))))
        .map_err(|e| to_py_err(py, e))
}

/// Parse a YAML file into plain Python objects (dicts, lists, scalars), like
/// ``yaml.full_load`` would.
#[pyfunction]
fn load_yaml(py: Python<'_>, path: PathBuf) -> PyResult<Py<PyAny>> {
    let value = py
        .detach(|| crate::yaml::parse_file(&path))
        .map_err(|e| to_py_err(py, e))?;
    Ok(Leaves::new(py, &[])?.plain(&value)?.unbind())
}

/// Build a config dataclass instance from a dict.
#[pyfunction]
#[pyo3(signature = (data, frozen = true))]
fn from_dict(py: Python<'_>, data: &Bound<'_, PyAny>, frozen: bool) -> PyResult<Py<PyAny>> {
    let mut externals = Vec::new();
    let value = from_py(data, &mut externals, 0)?;
    let Value::Map(map) = value else {
        return Err(PyTypeError::new_err(format!(
            "from_dict() expects a dict, got {}",
            data.get_type().name()?
        )));
    };
    let schema = Schema::infer(&map);
    ObjectBuilder::new(py, &schema, frozen, &externals)?.root(&map)
}

#[pymodule(name = "_core")]
fn core_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load_config, m)?)?;
    m.add_function(wrap_pyfunction!(generate_stub, m)?)?;
    m.add_function(wrap_pyfunction!(load_yaml, m)?)?;
    m.add_function(wrap_pyfunction!(from_dict, m)?)?;
    Ok(())
}
