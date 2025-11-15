use serde_json;
use serde_yaml;
use std::error::Error;

/// Convert any serializable value to a JSON dictionary (for debugging/inspection)
pub fn to_json_value<T: serde::Serialize>(config: &T) -> Result<serde_json::Value, Box<dyn Error>> {
    let json_string = serde_json::to_string(config)?;
    let value: serde_json::Value = serde_json::from_str(&json_string)?;
    Ok(value)
}

/// Convert any serializable value to YAML string
pub fn to_yaml_string<T: serde::Serialize>(config: &T) -> Result<String, Box<dyn Error>> {
    let yaml_string = serde_yaml::to_string(config)?;
    Ok(yaml_string)
}

/// Parse YAML from string into a value
pub fn from_yaml_str<T: serde::de::DeserializeOwned>(yaml: &str) -> Result<T, Box<dyn Error>> {
    let value: T = serde_yaml::from_str(yaml)?;
    Ok(value)
}

/// Load YAML from file
pub fn load_yaml_file(path: &std::path::Path) -> Result<serde_yaml::Value, Box<dyn Error>> {
    let content = std::fs::read_to_string(path)?;
    let value: serde_yaml::Value = serde_yaml::from_str(&content)?;
    Ok(value)
}

/// Write content to file
pub fn write_file(path: &std::path::Path, content: &str) -> Result<(), Box<dyn Error>> {
    std::fs::write(path, content)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde::{Deserialize, Serialize};

    #[derive(Debug, Serialize, Deserialize, PartialEq)]
    struct TestConfig {
        name: String,
        count: i64,
    }

    #[test]
    fn test_to_json_value() {
        let config = TestConfig {
            name: "test".to_string(),
            count: 42,
        };
        let json = to_json_value(&config).unwrap();
        assert_eq!(json["name"], "test");
        assert_eq!(json["count"], 42);
    }

    #[test]
    fn test_to_yaml_string() {
        let config = TestConfig {
            name: "test".to_string(),
            count: 42,
        };
        let yaml = to_yaml_string(&config).unwrap();
        assert!(yaml.contains("name: test"));
        assert!(yaml.contains("count: 42"));
    }

    #[test]
    fn test_from_yaml_str() {
        let yaml = "name: test\ncount: 42\n";
        let config: TestConfig = from_yaml_str(yaml).unwrap();
        assert_eq!(config.name, "test");
        assert_eq!(config.count, 42);
    }
}
