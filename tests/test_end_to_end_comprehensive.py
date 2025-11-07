"""
Comprehensive end-to-end tests for heracless
Testing complete workflows from YAML to config objects
"""

from datetime import date, datetime
from pathlib import Path

import pytest
import yaml

from heracless.fight import fight, load_as_dict
from heracless.utils import as_dict, from_dict, mutate_config
from heracless.utils.cfg_tree import tree_parser, tree_to_config_obj, tree_to_string_translator


class TestEndToEndBasicWorkflow:
    """Test basic end-to-end workflows"""

    def test_e2e_simple_config_load(self, tmp_path: Path) -> None:
        """Test loading a simple YAML config end-to-end"""
        # Create YAML file
        yaml_content = """
name: myapp
version: 1.0.0
port: 8080
debug: true
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        # Load config
        config = fight(config_file, stub_file, frozen=True)

        # Verify
        assert config.name == "myapp"
        assert config.version == "1.0.0"
        assert config.port == 8080
        assert config.debug is True
        assert stub_file.exists()

    def test_e2e_nested_config_load(self, tmp_path: Path) -> None:
        """Test loading nested YAML config"""
        yaml_content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret123
app:
  name: myapp
  settings:
    timeout: 30
    retries: 3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        config = fight(config_file, stub_file, frozen=True)

        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.database.credentials.username == "admin"
        assert config.database.credentials.password == "secret123"
        assert config.app.name == "myapp"
        assert config.app.settings.timeout == 30
        assert config.app.settings.retries == 3

    def test_e2e_with_lists(self, tmp_path: Path) -> None:
        """Test end-to-end with list values"""
        yaml_content = """
servers:
  - server1.example.com
  - server2.example.com
  - server3.example.com
ports:
  - 8080
  - 8081
  - 8082
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        config = fight(config_file, stub_file, frozen=True)

        assert len(config.servers) == 3
        assert config.servers[0] == "server1.example.com"
        assert config.servers[2] == "server3.example.com"
        assert len(config.ports) == 3
        assert config.ports[1] == 8081

    def test_e2e_with_mixed_types(self, tmp_path: Path) -> None:
        """Test end-to-end with various data types"""
        yaml_content = """
string_val: hello
int_val: 42
float_val: 3.14
bool_val: true
null_val: null
date_val: 2024-01-15
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        config = fight(config_file, stub_file, frozen=True)

        assert config.string_val == "hello"
        assert config.int_val == 42
        assert config.float_val == 3.14
        assert config.bool_val is True
        assert config.null_val is None
        # YAML parses date string as date object
        assert isinstance(config.date_val, date)


class TestEndToEndConfigManipulation:
    """Test config manipulation end-to-end"""

    def test_e2e_config_mutation(self, tmp_path: Path) -> None:
        """Test mutating config values"""
        yaml_content = """
name: original
value: 100
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        # Mutate config
        new_config = mutate_config(config, "name", "modified")
        assert new_config.name == "modified"
        assert config.name == "original"  # Original unchanged

        new_config2 = mutate_config(config, "value", 200)
        assert new_config2.value == 200
        assert config.value == 100  # Original unchanged

    def test_e2e_nested_mutation(self, tmp_path: Path) -> None:
        """Test mutating nested config values"""
        yaml_content = """
database:
  host: localhost
  port: 5432
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        # Mutate nested value
        new_config = mutate_config(config, "database.host", "remotehost")
        assert new_config.database.host == "remotehost"
        assert config.database.host == "localhost"

        new_config2 = mutate_config(config, "database.port", 3306)
        assert new_config2.database.port == 3306
        assert config.database.port == 5432

    def test_e2e_config_to_dict_conversion(self, tmp_path: Path) -> None:
        """Test converting config to dictionary"""
        yaml_content = """
name: test
nested:
  value: 42
  items:
    - a
    - b
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)
        config_dict = as_dict(config)

        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "test"
        assert config_dict["nested"]["value"] == 42
        assert config_dict["nested"]["items"][0] == "a"

    def test_e2e_dict_to_config_conversion(self, tmp_path: Path) -> None:
        """Test converting dictionary to config"""
        config_dict = {
            "name": "test",
            "value": 100,
            "nested": {"key": "value"},
        }

        config = from_dict(config_dict, frozen=True)

        assert config.name == "test"
        assert config.value == 100
        assert config.nested.key == "value"

    def test_e2e_round_trip_conversion(self, tmp_path: Path) -> None:
        """Test round-trip: config -> dict -> config"""
        yaml_content = """
name: test
value: 42
nested:
  key: value
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        # Load config
        config1 = fight(config_file, None, frozen=True)

        # Convert to dict
        config_dict = as_dict(config1)

        # Convert back to config
        config2 = from_dict(config_dict, frozen=True)

        # Verify they're equivalent
        assert config2.name == config1.name
        assert config2.value == config1.value
        assert config2.nested.key == config1.nested.key


class TestEndToEndStubGeneration:
    """Test stub file generation end-to-end"""

    def test_e2e_stub_file_generation(self, tmp_path: Path) -> None:
        """Test that stub file is generated correctly"""
        yaml_content = """
name: test
value: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        fight(config_file, stub_file, frozen=True)

        assert stub_file.exists()
        stub_content = stub_file.read_text()

        # Verify stub content
        assert "from dataclasses import dataclass" in stub_content
        assert "class Config:" in stub_content
        assert "name: str" in stub_content
        assert "value: int" in stub_content
        assert "def load_config" in stub_content

    def test_e2e_stub_with_nested_structures(self, tmp_path: Path) -> None:
        """Test stub generation with nested structures"""
        yaml_content = """
database:
  host: localhost
  port: 5432
app:
  name: myapp
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        fight(config_file, stub_file, frozen=True)

        stub_content = stub_file.read_text()

        # Should have multiple dataclasses
        assert "class Database:" in stub_content
        assert "class App:" in stub_content
        assert "class Config:" in stub_content

    def test_e2e_no_stub_generation(self, tmp_path: Path) -> None:
        """Test that no stub is generated when dump_dir is None"""
        yaml_content = """
name: test
value: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        assert config.name == "test"
        # No stub file should be created in tmp_path
        assert not any(f.suffix == ".pyi" for f in tmp_path.iterdir())


class TestEndToEndComplexScenarios:
    """Test complex real-world scenarios"""

    def test_e2e_large_config(self, tmp_path: Path) -> None:
        """Test with a larger, more realistic config"""
        yaml_content = """
application:
  name: MyApp
  version: 2.1.0
  environment: production

server:
  host: 0.0.0.0
  port: 8080
  workers: 4
  timeout: 300

database:
  primary:
    host: db-primary.example.com
    port: 5432
    database: myapp_prod
    ssl: true
  replica:
    host: db-replica.example.com
    port: 5432
    database: myapp_prod
    ssl: true

redis:
  host: redis.example.com
  port: 6379
  db: 0

logging:
  level: INFO
  format: json
  handlers:
    - console
    - file
    - syslog

features:
  feature_a: true
  feature_b: false
  feature_c: true

api_keys:
  service_a: abc123
  service_b: def456
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "types.pyi"

        config = fight(config_file, stub_file, frozen=True)

        # Verify various parts of the config
        assert config.application.name == "MyApp"
        assert config.application.version == "2.1.0"
        assert config.server.port == 8080
        assert config.server.workers == 4
        assert config.database.primary.host == "db-primary.example.com"
        assert config.database.replica.ssl is True
        assert config.redis.port == 6379
        assert config.logging.level == "INFO"
        assert len(config.logging.handlers) == 3
        assert "console" in config.logging.handlers
        assert config.features.feature_a is True
        assert config.features.feature_b is False
        assert config.api_keys.service_a == "abc123"

    def test_e2e_with_special_characters(self, tmp_path: Path) -> None:
        """Test config with special characters in keys"""
        yaml_content = """
test-name: value1
test_name: value2
test.name: value3
TestName: value4
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        # Special characters should be normalized
        assert hasattr(config, "test_name")

    def test_e2e_empty_config(self, tmp_path: Path) -> None:
        """Test with empty YAML file"""
        yaml_content = ""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        # Empty config should return None
        config = fight(config_file, None, frozen=True)
        assert config is None

    def test_e2e_list_of_dicts(self, tmp_path: Path) -> None:
        """Test with list of dictionaries"""
        yaml_content = """
users:
  - name: Alice
    age: 30
    email: alice@example.com
  - name: Bob
    age: 25
    email: bob@example.com
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        assert len(config.users) == 2
        assert config.users[0].name == "Alice"
        assert config.users[0].age == 30
        assert config.users[1].name == "Bob"
        assert config.users[1].email == "bob@example.com"


class TestEndToEndErrorHandling:
    """Test error handling in end-to-end scenarios"""

    def test_e2e_nonexistent_file(self) -> None:
        """Test loading non-existent file"""
        from heracless.utils.exceptions import DirectoryError

        with pytest.raises(DirectoryError):
            fight(Path("/nonexistent/config.yaml"), None, frozen=True)

    def test_e2e_invalid_yaml(self, tmp_path: Path) -> None:
        """Test with invalid YAML syntax"""
        from heracless.utils.exceptions import YamlSyntaxError

        yaml_content = """
name: test
  invalid: indentation
    bad: syntax
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        with pytest.raises(YamlSyntaxError):
            fight(config_file, None, frozen=True)

    def test_e2e_empty_file(self, tmp_path: Path) -> None:
        """Test with empty file"""
        config_file = tmp_path / "config.yaml"
        config_file.touch()  # Create empty file

        # Empty file should return None
        config = fight(config_file, None, frozen=True)
        assert config is None


class TestEndToEndMultiplePaths:
    """Test working with multiple config files"""

    def test_e2e_multiple_configs(self, tmp_path: Path) -> None:
        """Test loading multiple separate configs"""
        # Config 1
        yaml1 = """
name: config1
value: 100
"""
        config1_file = tmp_path / "config1.yaml"
        config1_file.write_text(yaml1)

        # Config 2
        yaml2 = """
name: config2
value: 200
"""
        config2_file = tmp_path / "config2.yaml"
        config2_file.write_text(yaml2)

        # Load both
        config1 = fight(config1_file, None, frozen=True)
        config2 = fight(config2_file, None, frozen=True)

        assert config1.name == "config1"
        assert config1.value == 100
        assert config2.name == "config2"
        assert config2.value == 200

    def test_e2e_config_with_path_object(self, tmp_path: Path) -> None:
        """Test that Path objects in config are preserved"""
        # Note: YAML doesn't natively support Path objects,
        # but strings can be used as paths
        yaml_content = """
file_path: /tmp/test.txt
data_dir: /var/data
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        # These will be strings from YAML
        assert config.file_path == "/tmp/test.txt"
        assert config.data_dir == "/var/data"


class TestEndToEndPerformance:
    """Test performance with various config sizes"""

    def test_e2e_deeply_nested_config(self, tmp_path: Path) -> None:
        """Test with deeply nested structure"""
        yaml_content = """
level1:
  level2:
    level3:
      level4:
        level5:
          level6:
            level7:
              level8:
                level9:
                  level10:
                    value: deep
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        # Navigate through all levels
        assert (
            config.level1.level2.level3.level4.level5.level6.level7.level8.level9.level10.value
            == "deep"
        )

    def test_e2e_wide_config(self, tmp_path: Path) -> None:
        """Test with many top-level keys"""
        # Generate config with many keys
        yaml_lines = ["---"]
        for i in range(100):
            yaml_lines.append(f"key_{i}: value_{i}")

        yaml_content = "\n".join(yaml_lines)
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = fight(config_file, None, frozen=True)

        # Verify some keys
        assert config.key_0 == "value_0"
        assert config.key_50 == "value_50"
        assert config.key_99 == "value_99"
