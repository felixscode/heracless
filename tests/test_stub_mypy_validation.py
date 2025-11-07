"""
Tests to verify generated stub files are mypy-valid
"""

import subprocess
from pathlib import Path

import pytest

from heracless.fight import fight


class TestStubMypyValidation:
    """Test that generated stub files pass mypy validation"""

    def test_simple_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that a simple stub file is mypy-valid"""
        yaml_content = """
name: test
version: 1.0.0
port: 8080
debug: true
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        config = fight(config_file, stub_file, frozen=True)
        assert stub_file.exists()

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_nested_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that a nested structure stub file is mypy-valid"""
        yaml_content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
app:
  name: myapp
  settings:
    timeout: 30
    retries: 3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_list_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that stub with lists is mypy-valid"""
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
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_complex_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that a complex stub file is mypy-valid"""
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
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_list_of_dicts_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that stub with list of dicts is mypy-valid"""
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
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_mixed_types_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that stub with mixed types is mypy-valid"""
        yaml_content = """
string_val: hello
int_val: 42
float_val: 3.14
bool_val: true
null_val: null
date_val: 2024-01-15
nested:
  inner_string: world
  inner_int: 100
list_of_strings:
  - one
  - two
  - three
list_of_ints:
  - 1
  - 2
  - 3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_deeply_nested_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that a deeply nested stub is mypy-valid"""
        yaml_content = """
level1:
  level2:
    level3:
      level4:
        level5:
          value: deep
          number: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"


class TestStubWithClientCode:
    """Test that generated stubs work correctly with client code"""

    def test_stub_with_client_code_mypy_valid(self, tmp_path: Path) -> None:
        """Test that client code using the stub passes mypy"""
        yaml_content = """
database:
  host: localhost
  port: 5432
app:
  name: myapp
  debug: true
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Create client code that uses the config
        client_code = """
from config_types import Config

def get_db_host(config: Config) -> str:
    return config.database.host

def get_app_name(config: Config) -> str:
    return config.app.name

def get_port(config: Config) -> int:
    return config.database.port

def is_debug(config: Config) -> bool:
    return config.app.debug
"""
        client_file = tmp_path / "client.py"
        client_file.write_text(client_code)

        # Run mypy on both stub and client code
        result = subprocess.run(
            ["mypy", str(stub_file), str(client_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed with: {result.stdout}\n{result.stderr}"

    def test_stub_content_structure(self, tmp_path: Path) -> None:
        """Test that stub file has correct structure"""
        yaml_content = """
name: test
value: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Read and verify stub content
        stub_content = stub_file.read_text()

        # Check for required imports
        assert "from dataclasses import dataclass" in stub_content
        assert "from datetime import datetime" in stub_content
        assert "from datetime import date" in stub_content
        assert "from pathlib import Path" in stub_content

        # Check for Config class
        assert "class Config:" in stub_content
        assert "name: str" in stub_content
        assert "value: int" in stub_content

        # Check for load_config function
        assert "def load_config" in stub_content

        # Verify it's properly formatted (black should have formatted it)
        # The content should be parseable Python
        result = subprocess.run(
            ["python", "-m", "py_compile", str(stub_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Stub file is not valid Python: {result.stderr}"


class TestStubEdgeCases:
    """Test edge cases in stub generation with mypy validation"""

    def test_special_chars_in_names_stub_mypy_valid(self, tmp_path: Path) -> None:
        """Test that special characters in names are handled correctly in stubs"""
        yaml_content = """
test-name: value1
test_value: value2
another-name: value3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        config = fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed: {result.stdout}\n{result.stderr}"

    def test_frozen_dataclass_in_stub(self, tmp_path: Path) -> None:
        """Test that frozen dataclasses are correctly specified in stub"""
        yaml_content = """
name: test
value: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub with frozen=True
        fight(config_file, stub_file, frozen=True)

        stub_content = stub_file.read_text()

        # Verify frozen parameter is set
        assert "@dataclass(frozen=True)" in stub_content

        # Run mypy
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed: {result.stdout}\n{result.stderr}"

    def test_non_frozen_dataclass_in_stub(self, tmp_path: Path) -> None:
        """Test that non-frozen dataclasses are correctly specified in stub"""
        yaml_content = """
name: test
value: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub with frozen=False
        fight(config_file, stub_file, frozen=False)

        stub_content = stub_file.read_text()

        # Verify frozen parameter is set to False
        assert "@dataclass(frozen=False)" in stub_content

        # Run mypy
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed: {result.stdout}\n{result.stderr}"


class TestStubWithRealWorldConfig:
    """Test stub generation with real-world config examples"""

    def test_django_style_config_stub(self, tmp_path: Path) -> None:
        """Test stub generation for Django-style configuration"""
        yaml_content = """
debug: true
secret_key: super-secret-key
allowed_hosts:
  - localhost
  - 127.0.0.1
  - example.com

database:
  engine: django.db.backends.postgresql
  name: mydb
  user: myuser
  password: mypass
  host: localhost
  port: 5432

cache:
  backend: django.core.cache.backends.redis.RedisCache
  location: redis://127.0.0.1:6379/1

installed_apps:
  - django.contrib.admin
  - django.contrib.auth
  - django.contrib.contenttypes
  - myapp
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        config = fight(config_file, stub_file, frozen=True)

        # Verify config values
        assert config.debug is True
        assert config.secret_key == "super-secret-key"
        assert len(config.allowed_hosts) == 3

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed: {result.stdout}\n{result.stderr}"

    def test_microservice_config_stub(self, tmp_path: Path) -> None:
        """Test stub generation for microservice configuration"""
        yaml_content = """
service:
  name: payment-service
  version: 1.2.3
  port: 8080

upstream_services:
  - name: user-service
    url: http://user-service:8081
  - name: order-service
    url: http://order-service:8082

database:
  connection_string: postgresql://user:pass@localhost/db
  pool_size: 10
  timeout: 30

monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 10
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        stub_file = tmp_path / "config_types.pyi"

        # Generate stub
        fight(config_file, stub_file, frozen=True)

        # Run mypy on stub file
        result = subprocess.run(
            ["mypy", str(stub_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"mypy failed: {result.stdout}\n{result.stderr}"
