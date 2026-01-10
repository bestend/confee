"""Tests for secret field masking functionality.

This module tests the SecretField feature which masks sensitive data
in configuration outputs to prevent accidental exposure in logs, prints, etc.
"""

import json

from confee import ConfigBase, SecretField


class SimpleConfig(ConfigBase):
    """Simple config with one secret field."""

    host: str
    password: str = SecretField(description="Database password")


class NestedConfig(ConfigBase):
    """Config with nested structure and secrets."""

    app_name: str
    api_key: str = SecretField(description="API key")


class ParentConfig(ConfigBase):
    """Parent config containing nested configs with secrets."""

    environment: str
    database: SimpleConfig
    service: NestedConfig


class MultiSecretConfig(ConfigBase):
    """Config with multiple secret fields."""

    username: str
    password: str = SecretField(description="Password")
    api_key: str = SecretField(description="API Key")
    token: str = SecretField(description="Auth token")
    public_url: str


class TestSecretFieldBasics:
    """Test basic SecretField functionality."""

    def test_secret_field_direct_access(self):
        """Test that direct attribute access returns actual value."""
        config = SimpleConfig(host="localhost", password="secret123")

        # Direct access should return the actual value
        assert config.password == "secret123"
        assert config.host == "localhost"

    def test_secret_field_in_model_dump(self):
        """Test that model_dump() returns actual values (not masked)."""
        config = SimpleConfig(host="localhost", password="secret123")
        data = config.model_dump()

        # Standard Pydantic dump should NOT mask
        assert data["password"] == "secret123"
        assert data["host"] == "localhost"

    def test_secret_field_in_to_dict(self):
        """Test that to_dict() returns actual values (not masked)."""
        config = SimpleConfig(host="localhost", password="secret123")
        data = config.to_dict()

        # to_dict is alias for model_dump, should NOT mask
        assert data["password"] == "secret123"
        assert data["host"] == "localhost"


class TestSecretMasking:
    """Test secret masking functionality."""

    def test_to_safe_dict_masks_secrets(self):
        """Test that to_safe_dict() masks secret fields."""
        config = SimpleConfig(host="localhost", password="secret123")
        safe_data = config.to_safe_dict()

        # Secret should be masked
        assert safe_data["password"] == "***MASKED***"
        # Normal field should be visible
        assert safe_data["host"] == "localhost"

    def test_to_safe_dict_custom_mask(self):
        """Test to_safe_dict() with custom mask string."""
        config = SimpleConfig(host="localhost", password="secret123")
        safe_data = config.to_safe_dict(mask="[REDACTED]")

        assert safe_data["password"] == "[REDACTED]"
        assert safe_data["host"] == "localhost"

    def test_to_safe_json_masks_secrets(self):
        """Test that to_safe_json() masks secret fields."""
        config = SimpleConfig(host="localhost", password="secret123")
        safe_json = config.to_safe_json()
        data = json.loads(safe_json)

        assert data["password"] == "***MASKED***"
        assert data["host"] == "localhost"

    def test_to_safe_json_custom_mask(self):
        """Test to_safe_json() with custom mask string."""
        config = SimpleConfig(host="localhost", password="secret123")
        safe_json = config.to_safe_json(mask="<HIDDEN>")
        data = json.loads(safe_json)

        assert data["password"] == "<HIDDEN>"
        assert data["host"] == "localhost"

    def test_to_safe_json_with_indent(self):
        """Test to_safe_json() with JSON formatting options."""
        config = SimpleConfig(host="localhost", password="secret123")
        safe_json = config.to_safe_json(indent=2)

        # Should be formatted JSON
        assert "\n" in safe_json
        data = json.loads(safe_json)
        assert data["password"] == "***MASKED***"


class TestMultipleSecrets:
    """Test masking when multiple secret fields exist."""

    def test_multiple_secrets_all_masked(self):
        """Test that all secret fields are masked."""
        config = MultiSecretConfig(
            username="admin",
            password="pass123",
            api_key="key456",
            token="token789",
            public_url="https://example.com",
        )
        safe_data = config.to_safe_dict()

        # All secrets should be masked
        assert safe_data["password"] == "***MASKED***"
        assert safe_data["api_key"] == "***MASKED***"
        assert safe_data["token"] == "***MASKED***"

        # Public fields should be visible
        assert safe_data["username"] == "admin"
        assert safe_data["public_url"] == "https://example.com"

    def test_empty_secret_field(self):
        """Test masking of empty secret fields."""
        config = MultiSecretConfig(
            username="admin",
            password="",  # Empty password
            api_key="key456",
            token="token789",
            public_url="https://example.com",
        )
        safe_data = config.to_safe_dict()

        # Even empty secrets should be masked
        assert safe_data["password"] == "***MASKED***"


class TestNestedSecrets:
    """Test secret masking in nested configurations."""

    def test_nested_config_secrets_masked(self):
        """Test that secrets in nested configs are masked."""
        config = ParentConfig(
            environment="production",
            database=SimpleConfig(host="db.example.com", password="dbpass123"),
            service=NestedConfig(app_name="myapp", api_key="apikey456"),
        )
        safe_data = config.to_safe_dict()

        # Check parent-level field
        assert safe_data["environment"] == "production"

        # Check nested secrets are masked
        assert safe_data["database"]["password"] == "***MASKED***"
        assert safe_data["service"]["api_key"] == "***MASKED***"

        # Check nested non-secrets are visible
        assert safe_data["database"]["host"] == "db.example.com"
        assert safe_data["service"]["app_name"] == "myapp"

    def test_deeply_nested_secrets(self):
        """Test masking in deeply nested structures."""

        # Create a 3-level nested structure
        class Level3(ConfigBase):
            secret: str = SecretField()
            public: str

        class Level2(ConfigBase):
            level3: Level3

        class Level1(ConfigBase):
            level2: Level2

        config = Level1(level2=Level2(level3=Level3(secret="deep_secret", public="visible")))

        safe_data = config.to_safe_dict()
        assert safe_data["level2"]["level3"]["secret"] == "***MASKED***"
        assert safe_data["level2"]["level3"]["public"] == "visible"


class TestSecretFieldMetadata:
    """Test SecretField metadata and schema generation."""

    def test_secret_field_has_metadata(self):
        """Test that SecretField adds x-secret metadata."""
        schema = SimpleConfig.model_json_schema()

        # Check that password field has secret metadata
        password_schema = schema["properties"]["password"]
        assert "x-secret" in password_schema
        assert password_schema["x-secret"] is True

        # Check that host field does NOT have secret metadata
        host_schema = schema["properties"]["host"]
        assert "x-secret" not in host_schema

    def test_secret_field_description(self):
        """Test that SecretField preserves description."""
        schema = SimpleConfig.model_json_schema()
        password_schema = schema["properties"]["password"]

        assert "description" in password_schema
        assert password_schema["description"] == "Database password"


class TestPrintSafe:
    """Test safe printing functionality."""

    def test_print_safe_masks_secrets(self, capsys):
        """Test that print(safe=True) masks secrets."""
        config = SimpleConfig(host="localhost", password="secret123")
        config.print(safe=True)

        captured = capsys.readouterr()
        output = captured.out

        # Should contain masked password
        assert "***MASKED***" in output
        # Should NOT contain actual password
        assert "secret123" not in output
        # Should contain host
        assert "localhost" in output

    def test_print_unsafe_shows_secrets(self, capsys):
        """Test that print(safe=False) shows actual values."""
        config = SimpleConfig(host="localhost", password="secret123")
        config.print(safe=False)

        captured = capsys.readouterr()
        output = captured.out

        # Should contain actual password
        assert "secret123" in output
        assert "localhost" in output


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_secret_field_with_none_default(self):
        """Test SecretField with None as default value."""

        class OptionalSecretConfig(ConfigBase):
            optional_secret: str | None = SecretField(default=None)

        config = OptionalSecretConfig()
        safe_data = config.to_safe_dict()

        # None should still be masked
        assert safe_data["optional_secret"] == "***MASKED***"

    def test_secret_field_with_special_characters(self):
        """Test SecretField with special characters in value."""
        special_password = "p@ssw0rd!#$%^&*()"
        config = SimpleConfig(host="localhost", password=special_password)

        # Direct access should work
        assert config.password == special_password

        # Should be masked in safe methods
        safe_data = config.to_safe_dict()
        assert safe_data["password"] == "***MASKED***"

    def test_config_without_secrets(self):
        """Test config with no secret fields."""

        class NoSecretConfig(ConfigBase):
            name: str
            value: int

        config = NoSecretConfig(name="test", value=42)
        safe_data = config.to_safe_dict()

        # All fields should be visible (no masking)
        assert safe_data["name"] == "test"
        assert safe_data["value"] == 42

    def test_list_of_secrets(self):
        """Test masking of lists containing sensitive data."""

        class ListConfig(ConfigBase):
            passwords: list[str] = SecretField(default_factory=list)

        config = ListConfig(passwords=["pass1", "pass2", "pass3"])
        safe_data = config.to_safe_dict()

        # List field is masked (implementation masks each item in list)
        assert safe_data["passwords"] == ["***MASKED***", "***MASKED***", "***MASKED***"]

    def test_list_of_configbase_with_secrets(self):
        """Test masking secrets in list of nested ConfigBase objects."""

        class DbConfig(ConfigBase):
            host: str
            password: str = SecretField()

        class AppConfig(ConfigBase):
            databases: list[DbConfig]

        config = AppConfig(
            databases=[
                DbConfig(host="db1.example.com", password="pass1"),
                DbConfig(host="db2.example.com", password="pass2"),
            ]
        )
        safe_data = config.to_safe_dict()

        assert safe_data["databases"][0]["host"] == "db1.example.com"
        assert safe_data["databases"][0]["password"] == "***MASKED***"
        assert safe_data["databases"][1]["host"] == "db2.example.com"
        assert safe_data["databases"][1]["password"] == "***MASKED***"
