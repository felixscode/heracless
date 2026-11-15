//! Type inference: from a parsed config to a set of named classes with typed fields.
//!
//! Inference happens in two passes:
//!
//! 1. Every value is reduced to a [`Shape`]. Shapes of list items are merged, so a
//!    list of mappings yields *one* item shape whose fields are the union of all
//!    items' keys (keys missing from some items become optional).
//! 2. Shapes are resolved into [`Ty`]s, turning each mapping shape into a [`Class`].
//!    Classes are created bottom-up; two mappings that would get the same class
//!    name share one class when they are structurally identical, and get distinct
//!    names (`OtherServer`, `Server2`, ...) when they are not.

use std::collections::HashSet;

use indexmap::IndexMap;

use crate::naming::{to_pascal_case, to_snake_case};
use crate::value::{ExternalKind, Map, Value};

/// Name of the class generated for the document root.
pub const ROOT_CLASS: &str = "Config";

/// Index of a class in [`Schema::classes`].
pub type ClassId = usize;

/// The inferred type of a field.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Ty {
    Any,
    None,
    Bool,
    Int,
    Float,
    Str,
    Date,
    DateTime,
    /// A homogeneous, variable-length sequence (a `tuple[T, ...]` in Python).
    List(Box<Ty>),
    Class(ClassId),
    /// Two or more alternatives; never nested, never containing `Any`.
    Union(Vec<Ty>),
}

impl Ty {
    /// `T` -> `T | None`.
    fn optional(self) -> Ty {
        match self {
            Ty::Any | Ty::None => self,
            Ty::Union(mut members) => {
                if !members.contains(&Ty::None) {
                    members.push(Ty::None);
                }
                Ty::Union(members)
            }
            other => Ty::Union(vec![other, Ty::None]),
        }
    }

    /// The class a mapping value of this type is built from.
    pub fn class_id(&self) -> Option<ClassId> {
        match self {
            Ty::Class(id) => Some(*id),
            Ty::Union(members) => members.iter().find_map(Ty::class_id),
            _ => None,
        }
    }

    /// The element type a sequence value of this type holds.
    pub fn element(&self) -> Option<&Ty> {
        match self {
            Ty::List(element) => Some(element),
            Ty::Union(members) => members.iter().find_map(Ty::element),
            _ => None,
        }
    }

    /// Every class referenced by this type, in order of appearance.
    fn visit_classes(&self, f: &mut impl FnMut(ClassId)) {
        match self {
            Ty::Class(id) => f(*id),
            Ty::List(element) => element.visit_classes(f),
            Ty::Union(members) => members.iter().for_each(|m| m.visit_classes(f)),
            _ => {}
        }
    }
}

/// A field of a generated class.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Field {
    /// The key as written in the YAML document.
    pub key: String,
    /// The attribute name: a valid, unique Python identifier derived from `key`.
    pub name: String,
    pub ty: Ty,
}

/// A generated class (one per distinct mapping shape).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Class {
    pub name: String,
    pub fields: Vec<Field>,
}

/// The classes describing a config. The root class is always named [`ROOT_CLASS`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Schema {
    classes: Vec<Class>,
    root: ClassId,
}

impl Schema {
    /// Infer the schema of a config document.
    pub fn infer(root: &Map) -> Schema {
        let mut resolver = Resolver::default();
        let root_shape = shape_of_map(root);
        // Children of the root are disambiguated numerically (`Server2`), not as `ConfigServer`.
        let fields = resolver.resolve_fields(root_shape, None);
        resolver.classes.push(Class {
            name: ROOT_CLASS.to_string(),
            fields,
        });
        let root = resolver.classes.len() - 1;
        Schema {
            classes: resolver.classes,
            root,
        }
    }

    pub fn root(&self) -> ClassId {
        self.root
    }

    pub fn class(&self, id: ClassId) -> &Class {
        &self.classes[id]
    }

    pub fn len(&self) -> usize {
        self.classes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.classes.is_empty()
    }

    /// Classes in reading order: the root first, then each class the first time a
    /// field refers to it (depth-first). This mirrors the layout of the YAML file.
    pub fn ordered(&self) -> Vec<ClassId> {
        fn visit(schema: &Schema, id: ClassId, seen: &mut Vec<bool>, out: &mut Vec<ClassId>) {
            if std::mem::replace(&mut seen[id], true) {
                return;
            }
            out.push(id);
            for field in &schema.classes[id].fields {
                field
                    .ty
                    .visit_classes(&mut |child| visit(schema, child, seen, out));
            }
        }
        let mut seen = vec![false; self.classes.len()];
        let mut out = Vec::with_capacity(self.classes.len());
        visit(self, self.root, &mut seen, &mut out);
        out
    }
}

/// Structural description of a value, before classes are named.
#[derive(Debug, Clone, PartialEq)]
enum Shape {
    /// Nothing is known (the items of an empty list).
    Unknown,
    Any,
    None,
    Bool,
    Int,
    Float,
    Str,
    Date,
    DateTime,
    List(Box<Shape>),
    /// Field shapes keyed by YAML key; the flag marks fields missing from some instances.
    Map(IndexMap<String, (Shape, bool)>),
    Union(Vec<Shape>),
}

fn shape_of(value: &Value) -> Shape {
    match value {
        Value::Null => Shape::None,
        Value::Bool(_) => Shape::Bool,
        Value::Int(_) | Value::BigInt(_) => Shape::Int,
        Value::Float(_) => Shape::Float,
        Value::Str(_) => Shape::Str,
        Value::Date(_) => Shape::Date,
        Value::DateTime(_) => Shape::DateTime,
        Value::Seq(items) => Shape::List(Box::new(
            items.iter().map(shape_of).fold(Shape::Unknown, merge),
        )),
        Value::Map(map) => shape_of_map(map),
        Value::External { kind, .. } => match kind {
            ExternalKind::Date => Shape::Date,
            ExternalKind::DateTime => Shape::DateTime,
            ExternalKind::Any => Shape::Any,
        },
    }
}

fn shape_of_map(map: &Map) -> Shape {
    Shape::Map(
        map.iter()
            .map(|(k, v)| (k.clone(), (shape_of(v), false)))
            .collect(),
    )
}

/// Shapes that merge into one (rather than forming a union).
fn same_kind(a: &Shape, b: &Shape) -> bool {
    let numeric = |s: &Shape| matches!(s, Shape::Int | Shape::Float);
    std::mem::discriminant(a) == std::mem::discriminant(b) || (numeric(a) && numeric(b))
}

fn merge(a: Shape, b: Shape) -> Shape {
    match (a, b) {
        (Shape::Unknown, x) | (x, Shape::Unknown) => x,
        (Shape::Any, _) | (_, Shape::Any) => Shape::Any,
        (Shape::Union(mut members), Shape::Union(others)) => {
            others.into_iter().for_each(|o| add_member(&mut members, o));
            Shape::Union(members)
        }
        (Shape::Union(mut members), other) => {
            add_member(&mut members, other);
            Shape::Union(members)
        }
        (other, Shape::Union(members)) => {
            let mut merged = vec![other];
            members.into_iter().for_each(|m| add_member(&mut merged, m));
            Shape::Union(merged)
        }
        (a, b) if same_kind(&a, &b) => merge_same_kind(a, b),
        (a, b) => Shape::Union(vec![a, b]),
    }
}

fn add_member(members: &mut Vec<Shape>, shape: Shape) {
    match members.iter_mut().find(|m| same_kind(m, &shape)) {
        Some(member) => {
            let current = std::mem::replace(member, Shape::Unknown);
            *member = merge_same_kind(current, shape);
        }
        None => members.push(shape),
    }
}

fn merge_same_kind(a: Shape, b: Shape) -> Shape {
    match (a, b) {
        (Shape::Int, Shape::Int) => Shape::Int,
        (Shape::Int | Shape::Float, Shape::Int | Shape::Float) => Shape::Float,
        (Shape::List(a), Shape::List(b)) => Shape::List(Box::new(merge(*a, *b))),
        (Shape::Map(mut a), Shape::Map(b)) => {
            for (key, (_, optional)) in a.iter_mut() {
                if !b.contains_key(key) {
                    *optional = true;
                }
            }
            for (key, (shape, optional)) in b {
                match a.get_mut(&key) {
                    Some((existing, existing_optional)) => {
                        let current = std::mem::replace(existing, Shape::Unknown);
                        *existing = merge(current, shape);
                        *existing_optional |= optional;
                    }
                    None => {
                        a.insert(key, (shape, true));
                    }
                }
            }
            Shape::Map(a)
        }
        (a, _) => a,
    }
}

#[derive(Default)]
struct Resolver {
    classes: Vec<Class>,
}

impl Resolver {
    /// Resolve a shape found under key `hint` inside the class named `parent`.
    fn resolve(&mut self, shape: Shape, hint: &str, parent: Option<&str>) -> Ty {
        match shape {
            Shape::Unknown | Shape::Any => Ty::Any,
            Shape::None => Ty::None,
            Shape::Bool => Ty::Bool,
            Shape::Int => Ty::Int,
            Shape::Float => Ty::Float,
            Shape::Str => Ty::Str,
            Shape::Date => Ty::Date,
            Shape::DateTime => Ty::DateTime,
            Shape::List(element) => Ty::List(Box::new(self.resolve(
                *element,
                &format!("{hint}_item"),
                parent,
            ))),
            Shape::Union(members) => {
                let mut tys: Vec<Ty> = Vec::with_capacity(members.len());
                for member in members {
                    let ty = self.resolve(member, hint, parent);
                    if !tys.contains(&ty) {
                        tys.push(ty);
                    }
                }
                if tys.len() == 1 {
                    tys.pop().unwrap()
                } else {
                    Ty::Union(tys)
                }
            }
            map @ Shape::Map(_) => {
                let name = to_pascal_case(hint);
                let fields = self.resolve_fields(map, Some(&name));
                Ty::Class(self.intern(name, parent, fields))
            }
        }
    }

    /// Resolve the fields of a mapping shape. `owner` is the (preferred) name of the
    /// class being built, used to disambiguate the names of nested classes.
    fn resolve_fields(&mut self, shape: Shape, owner: Option<&str>) -> Vec<Field> {
        let Shape::Map(entries) = shape else {
            unreachable!("resolve_fields called on a non-mapping shape")
        };
        let mut used = HashSet::with_capacity(entries.len());
        entries
            .into_iter()
            .map(|(key, (shape, optional))| {
                let mut ty = self.resolve(shape, &key, owner);
                if optional {
                    ty = ty.optional();
                }
                let name = unique_attribute(&key, &mut used);
                Field { key, name, ty }
            })
            .collect()
    }

    /// Find or create the class for `fields`, picking a name that is free (or taken
    /// by an identical class, which is then shared).
    fn intern(&mut self, preferred: String, parent: Option<&str>, fields: Vec<Field>) -> ClassId {
        let candidates = std::iter::once(preferred.clone())
            .chain(parent.map(|p| format!("{p}{preferred}")))
            .chain((2..).map(|n| format!("{preferred}{n}")));
        for candidate in candidates {
            if candidate == ROOT_CLASS {
                continue;
            }
            match self.classes.iter().position(|c| c.name == candidate) {
                Some(id) if self.classes[id].fields == fields => return id,
                Some(_) => continue,
                None => {
                    self.classes.push(Class {
                        name: candidate,
                        fields,
                    });
                    return self.classes.len() - 1;
                }
            }
        }
        unreachable!("the candidate name iterator is infinite")
    }
}

/// Attribute name for `key`, made unique among its siblings with `_1`, `_2`, ...
fn unique_attribute(key: &str, used: &mut HashSet<String>) -> String {
    let base = to_snake_case(key);
    let mut name = base.clone();
    let mut n = 1;
    while used.contains(&name) {
        name = format!("{base}_{n}");
        n += 1;
    }
    used.insert(name.clone());
    name
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::yaml::parse_str;
    use pretty_assertions::assert_eq;

    fn schema(src: &str) -> Schema {
        match parse_str(src).unwrap() {
            Value::Map(map) => Schema::infer(&map),
            other => panic!("not a mapping: {other:?}"),
        }
    }

    fn class_names(s: &Schema) -> Vec<&str> {
        s.ordered()
            .into_iter()
            .map(|id| s.class(id).name.as_str())
            .collect()
    }

    fn field<'a>(s: &'a Schema, class: &str, name: &str) -> &'a Field {
        let id = (0..s.len()).find(|&id| s.class(id).name == class).unwrap();
        s.class(id).fields.iter().find(|f| f.name == name).unwrap()
    }

    #[test]
    fn identical_nested_mappings_share_a_class() {
        let s = schema("a:\n  address: {city: x}\nb:\n  address: {city: y}\n");
        assert_eq!(class_names(&s), ["Config", "A", "Address", "B"]);
    }

    #[test]
    fn conflicting_class_names_are_disambiguated() {
        let s = schema(
            "server: {host: h}\nother:\n  server: {name: n}\nthird:\n  x:\n    server: {port: 1}\n",
        );
        assert_eq!(
            class_names(&s),
            [
                "Config",
                "Server",
                "Other",
                "OtherServer",
                "Third",
                "X",
                "XServer"
            ]
        );
    }

    #[test]
    fn nested_config_key_does_not_clash_with_root() {
        let s = schema("config: {a: 1}\n");
        assert_eq!(class_names(&s), ["Config", "Config2"]);
    }

    #[test]
    fn list_items_are_merged_and_missing_keys_are_optional() {
        let s = schema("users:\n  - {name: a, age: 1}\n  - {name: b, email: e}\n");
        assert_eq!(
            field(&s, "Config", "users").ty,
            Ty::List(Box::new(Ty::Class(0)))
        );
        assert_eq!(field(&s, "UsersItem", "name").ty, Ty::Str);
        assert_eq!(
            field(&s, "UsersItem", "age").ty,
            Ty::Union(vec![Ty::Int, Ty::None])
        );
        assert_eq!(
            field(&s, "UsersItem", "email").ty,
            Ty::Union(vec![Ty::Str, Ty::None])
        );
    }

    #[test]
    fn mixed_lists_become_unions_and_ints_widen_to_float() {
        let s = schema("a: [1, x, 2]\nb: [1, 2.5]\nc: []\nd: [1, ~]\n");
        assert_eq!(
            field(&s, "Config", "a").ty,
            Ty::List(Box::new(Ty::Union(vec![Ty::Int, Ty::Str])))
        );
        assert_eq!(field(&s, "Config", "b").ty, Ty::List(Box::new(Ty::Float)));
        assert_eq!(field(&s, "Config", "c").ty, Ty::List(Box::new(Ty::Any)));
        assert_eq!(
            field(&s, "Config", "d").ty,
            Ty::List(Box::new(Ty::Union(vec![Ty::Int, Ty::None])))
        );
    }

    #[test]
    fn colliding_attribute_names_are_deduplicated() {
        let s = schema("my-key: 1\nmy_key: 2\nmyKey: 3\nclass: 4\n");
        let names: Vec<_> = s
            .class(s.root())
            .fields
            .iter()
            .map(|f| f.name.as_str())
            .collect();
        assert_eq!(names, ["my_key", "my_key_1", "my_key_2", "class_"]);
    }
}
