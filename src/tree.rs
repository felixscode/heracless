use heck::{ToSnakeCase, ToPascalCase};
use regex::Regex;
use serde_yaml::Value;

/// Represents a leaf node in the configuration tree (primitive value)
#[derive(Debug, Clone, PartialEq)]
pub struct Leaf {
    pub name: String,
    pub type_name: String,
    pub value: Value,
}

/// Represents a structure node in the configuration tree (complex type)
#[derive(Debug, Clone, PartialEq)]
pub struct Structure {
    pub name: String,
    pub type_name: String,
    pub children: Vec<Node>,
}

/// Represents a node in the configuration tree (either Leaf or Structure)
#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    Leaf(Leaf),
    Structure(Structure),
}

impl Node {
    pub fn name(&self) -> &str {
        match self {
            Node::Leaf(leaf) => &leaf.name,
            Node::Structure(structure) => &structure.name,
        }
    }

    pub fn type_name(&self) -> &str {
        match self {
            Node::Leaf(leaf) => &leaf.type_name,
            Node::Structure(structure) => &structure.type_name,
        }
    }
}

/// Represents the root of the configuration tree
#[derive(Debug, Clone, PartialEq)]
pub struct Tree {
    pub name: String,
    pub children: Vec<Node>,
}

/// Replace invalid characters in names with underscores
pub fn replace_invalid_names(name: &str) -> String {
    let re = Regex::new(r"[^a-zA-Z0-9_]").unwrap();
    re.replace_all(name, "_").to_string()
}

/// Convert name to snake_case for field names
pub fn to_snake_case(name: &str) -> String {
    let sanitized = replace_invalid_names(name);
    sanitized.to_snake_case()
}

/// Convert name to PascalCase for type names
pub fn to_pascal_case(name: &str) -> String {
    let sanitized = replace_invalid_names(name);
    sanitized.to_pascal_case()
}

/// Infer the Rust type name from a YAML value
pub fn infer_type_name(value: &Value) -> String {
    match value {
        Value::Null => "Option<String>".to_string(),
        Value::Bool(_) => "bool".to_string(),
        Value::Number(n) => {
            if n.is_i64() {
                "i64".to_string()
            } else if n.is_u64() {
                "u64".to_string()
            } else {
                "f64".to_string()
            }
        }
        Value::String(_) => "String".to_string(),
        Value::Sequence(_) => "Vec".to_string(),
        Value::Mapping(_) => "Mapping".to_string(),
        Value::Tagged(_) => "Value".to_string(),
    }
}

/// Build a tree from a YAML value
pub fn build_tree(name: String, value: &Value) -> Result<Node, String> {
    match value {
        Value::Mapping(map) => {
            let mut children = Vec::new();
            for (key, val) in map {
                let key_str = match key {
                    Value::String(s) => s.clone(),
                    _ => key.as_str().unwrap_or("unknown").to_string(),
                };
                children.push(build_tree(key_str, val)?);
            }
            Ok(Node::Structure(Structure {
                name: name.clone(),
                type_name: "Mapping".to_string(),
                children,
            }))
        }
        Value::Sequence(seq) => {
            let mut children = Vec::new();
            if let Some(first) = seq.first() {
                // Build a representative child for type inference
                let item_name = format!("{}_item", name);
                children.push(build_tree(item_name, first)?);
            }
            Ok(Node::Structure(Structure {
                name: name.clone(),
                type_name: "Vec".to_string(),
                children,
            }))
        }
        _ => {
            // Leaf node
            let type_name = infer_type_name(value);
            Ok(Node::Leaf(Leaf {
                name: name.clone(),
                type_name,
                value: value.clone(),
            }))
        }
    }
}

/// Parse a YAML mapping into a Tree
pub fn parse_tree(value: &Value) -> Result<Tree, String> {
    match value {
        Value::Mapping(_) => {
            let node = build_tree("Config".to_string(), value)?;
            match node {
                Node::Structure(structure) => Ok(Tree {
                    name: structure.name,
                    children: structure.children,
                }),
                _ => Err("Expected mapping at root level".to_string()),
            }
        }
        _ => Err("Root value must be a mapping".to_string()),
    }
}

/// Iterate over all structures in a tree (for code generation)
pub fn iterate_structures(node: &Node) -> Vec<&Structure> {
    let mut result = Vec::new();
    match node {
        Node::Structure(structure) => {
            if structure.type_name == "Mapping" {
                result.push(structure);
            }
            for child in &structure.children {
                result.extend(iterate_structures(child));
            }
        }
        Node::Leaf(_) => {}
    }
    result
}

pub fn iterate_tree_structures(tree: &Tree) -> Vec<&Structure> {
    let mut result = Vec::new();
    for child in &tree.children {
        result.extend(iterate_structures(child));
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_replace_invalid_names() {
        assert_eq!(replace_invalid_names("test-name"), "test_name");
        assert_eq!(replace_invalid_names("test.name"), "test_name");
    }

    #[test]
    fn test_to_snake_case() {
        assert_eq!(to_snake_case("TestName"), "test_name");
        assert_eq!(to_snake_case("test-name"), "test_name");
    }

    #[test]
    fn test_to_pascal_case() {
        assert_eq!(to_pascal_case("test_name"), "TestName");
        assert_eq!(to_pascal_case("test-name"), "TestName");
    }

    #[test]
    fn test_infer_type_name() {
        assert_eq!(infer_type_name(&Value::Bool(true)), "bool");
        assert_eq!(infer_type_name(&Value::Number(42.into())), "i64");
        assert_eq!(infer_type_name(&Value::String("test".into())), "String");
    }
}
