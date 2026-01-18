"""Tests for confee.overrides module - CLI and environment variable overrides."""

import os

import pytest

from confee import ConfigBase, OverrideHandler


class SampleConfig(ConfigBase):
    """Sample configuration for testing."""

    name: str
    debug: bool = False
    workers: int = 4
    timeout: float = 30.5


class TestParseOverrideString:
    """Test parsing override strings."""

    def test_parse_simple_override(self):
        """Test parsing simple key=value override."""
        key, value = OverrideHandler.parse_override_string("debug=true")
        assert key == "debug"
        assert value == "true"

    def test_parse_override_with_spaces(self):
        """Test that spaces are stripped."""
        key, value = OverrideHandler.parse_override_string(" debug = true ")
        assert key == "debug"
        assert value == "true"

    def test_parse_override_with_multiple_equals(self):
        """Test parsing value with multiple equals signs."""
        key, value = OverrideHandler.parse_override_string("connection=user:pass@host=localhost")
        assert key == "connection"
        assert value == "user:pass@host=localhost"

    def test_parse_invalid_format(self):
        """Test that invalid format raises error."""
        with pytest.raises(ValueError):
            OverrideHandler.parse_override_string("no_equals_sign")


class TestParseOverrides:
    """Test parsing multiple override strings."""

    def test_parse_multiple_overrides(self):
        """Test parsing multiple override strings."""
        overrides = OverrideHandler.parse_overrides(["debug=true", "workers=8", "timeout=60.5"])

        assert overrides["debug"] == "true"
        assert overrides["workers"] == "8"
        assert overrides["timeout"] == "60.5"

    def test_parse_empty_list(self):
        """Test parsing empty override list."""
        overrides = OverrideHandler.parse_overrides([])
        assert overrides == {}


class TestValueCoercion:
    """Test value type coercion."""

    def test_coerce_to_bool_true(self):
        """Test coercion to boolean (true variations)."""
        assert OverrideHandler.coerce_value("true", bool) is True
        assert OverrideHandler.coerce_value("True", bool) is True
        assert OverrideHandler.coerce_value("TRUE", bool) is True
        assert OverrideHandler.coerce_value("yes", bool) is True
        assert OverrideHandler.coerce_value("1", bool) is True
        assert OverrideHandler.coerce_value("on", bool) is True

    def test_coerce_to_bool_false(self):
        """Test coercion to boolean (false values)."""
        assert OverrideHandler.coerce_value("false", bool) is False
        assert OverrideHandler.coerce_value("0", bool) is False
        assert OverrideHandler.coerce_value("no", bool) is False
        assert OverrideHandler.coerce_value("off", bool) is False

    def test_coerce_to_bool_invalid(self):
        """Test coercion to boolean with invalid values."""
        with pytest.raises(ValueError):
            OverrideHandler.coerce_value("anything_else", bool)

    def test_coerce_to_int(self):
        """Test coercion to integer."""
        assert OverrideHandler.coerce_value("42", int) == 42
        assert OverrideHandler.coerce_value("-10", int) == -10

    def test_coerce_to_float(self):
        """Test coercion to float."""
        assert OverrideHandler.coerce_value("3.14", float) == 3.14
        assert OverrideHandler.coerce_value("1.0", float) == 1.0

    def test_coerce_to_string(self):
        """Test coercion to string."""
        assert OverrideHandler.coerce_value("hello", str) == "hello"


class TestApplyOverrides:
    """Test applying overrides to configuration."""

    def test_apply_single_override(self):
        """Test applying single override."""
        config = SampleConfig(name="original")
        overrides = {"debug": "true"}

        updated = OverrideHandler.apply_overrides(config, overrides)

        assert updated.name == "original"
        assert updated.debug is True

    def test_apply_multiple_overrides(self):
        """Test applying multiple overrides."""
        config = SampleConfig(name="original", debug=False, workers=4)
        overrides = {"debug": "true", "workers": "16"}

        updated = OverrideHandler.apply_overrides(config, overrides)

        assert updated.name == "original"
        assert updated.debug is True
        assert updated.workers == 16

    def test_apply_override_with_type_inference(self):
        """Test that types are inferred from current config."""
        config = SampleConfig(name="test")
        overrides = {"timeout": "60.5"}

        updated = OverrideHandler.apply_overrides(config, overrides)

        assert updated.timeout == 60.5
        assert isinstance(updated.timeout, float)

    def test_apply_override_unknown_key_non_strict(self):
        """Test applying override with unknown key in non-strict mode."""
        config = SampleConfig(name="test")
        overrides = {"unknown_key": "value"}

        # Should not raise error in non-strict mode (strict=False by default)
        updated = OverrideHandler.apply_overrides(config, overrides, strict=False)
        assert updated.name == "test"

    def test_apply_override_unknown_key_strict(self):
        """Test applying override with unknown key in strict mode."""
        config = SampleConfig(name="test")
        overrides = {"unknown_key": "value"}

        with pytest.raises(KeyError):
            OverrideHandler.apply_overrides(config, overrides, strict=True)


class TestGetEnvOverrides:
    """Test getting overrides from environment variables."""

    def test_get_env_overrides_default_prefix(self):
        """Test getting overrides with default CONFEE_ prefix."""
        os.environ["CONFEE_DEBUG"] = "true"
        os.environ["CONFEE_WORKERS"] = "8"
        os.environ["OTHER_VAR"] = "ignored"

        try:
            overrides = OverrideHandler.get_env_overrides()

            assert "debug" in overrides
            assert overrides["debug"] == "true"
            assert "workers" in overrides
            assert overrides["workers"] == "8"
            assert "other_var" not in overrides
        finally:
            del os.environ["CONFEE_DEBUG"]
            del os.environ["CONFEE_WORKERS"]
            del os.environ["OTHER_VAR"]

    def test_get_env_overrides_custom_prefix(self):
        """Test getting overrides with custom prefix."""
        os.environ["MYAPP_DEBUG"] = "false"
        os.environ["MYAPP_NAME"] = "test"

        try:
            overrides = OverrideHandler.get_env_overrides(prefix="MYAPP_")

            assert overrides["debug"] == "false"
            assert overrides["name"] == "test"
        finally:
            del os.environ["MYAPP_DEBUG"]
            del os.environ["MYAPP_NAME"]

    def test_get_env_overrides_empty(self):
        """Test getting env overrides when no matching variables exist."""
        # Make sure no CONFEE_ variables exist
        for key in list(os.environ.keys()):
            if key.startswith("CONFEE_"):
                del os.environ[key]

        overrides = OverrideHandler.get_env_overrides()
        assert overrides == {} or all(not v.startswith("CONFEE_") for v in os.environ)


class TestFromCliAndEnv:
    """Test creating config from CLI and environment variables."""

    def test_from_cli_and_env_cli_only(self):
        """Test creating config from CLI arguments only."""
        config = OverrideHandler.from_cli_and_env(
            SampleConfig, cli_overrides=["name=cli_app", "debug=true"]
        )

        assert config.name == "cli_app"
        assert config.debug is True
        assert config.workers == 4  # default

    def test_from_cli_and_env_env_only(self):
        """Test creating config from environment variables only."""
        os.environ["CONFEE_NAME"] = "env_app"
        os.environ["CONFEE_DEBUG"] = "true"

        try:
            config = OverrideHandler.from_cli_and_env(SampleConfig, env_prefix="CONFEE_")

            assert config.name == "env_app"
            assert config.debug is True
        finally:
            del os.environ["CONFEE_NAME"]
            del os.environ["CONFEE_DEBUG"]

    def test_from_cli_and_env_cli_overrides_env(self):
        """Test that CLI arguments override environment variables."""
        os.environ["CONFEE_NAME"] = "env_app"
        os.environ["CONFEE_DEBUG"] = "false"

        try:
            config = OverrideHandler.from_cli_and_env(
                SampleConfig, cli_overrides=["debug=true"], env_prefix="CONFEE_"
            )

            assert config.name == "env_app"  # From env
            assert config.debug is True  # From CLI (overrides env)
        finally:
            del os.environ["CONFEE_NAME"]
            del os.environ["CONFEE_DEBUG"]

    def test_from_cli_and_env_explicit_env_dict(self):
        """Test using explicit env overrides dictionary."""
        config = OverrideHandler.from_cli_and_env(
            SampleConfig, env_overrides={"name": "explicit_app", "workers": "16"}
        )

        assert config.name == "explicit_app"
        assert config.workers == 16


class TestOverridePriority:
    """Test override priority order."""

    def test_priority_cli_over_env(self):
        """Test that CLI overrides take precedence over environment."""
        os.environ["CONFEE_NAME"] = "env_app"
        os.environ["CONFEE_DEBUG"] = "false"
        os.environ["CONFEE_WORKERS"] = "4"

        try:
            config = OverrideHandler.from_cli_and_env(
                SampleConfig,
                cli_overrides=["debug=true"],  # Higher priority
                env_prefix="CONFEE_",
            )

            # CLI override wins
            assert config.debug is True
            # Env values used where no CLI override
            assert config.name == "env_app"
            assert config.workers == 4
        finally:
            del os.environ["CONFEE_NAME"]
            del os.environ["CONFEE_DEBUG"]
            del os.environ["CONFEE_WORKERS"]


class TestOverrideMatrix:
    """Integration tests for override handling."""

    def test_apply_overrides_strict_unknown_key_raises(self):
        """Test that unknown keys raise error in strict mode."""
        cfg = SampleConfig(name="test")
        with pytest.raises(KeyError):
            OverrideHandler.apply_overrides(cfg, {"unknown": "x"}, strict=True)

    def test_coerce_value_bool_invalid(self):
        """Test that invalid boolean values raise error."""
        with pytest.raises(ValueError) as ei:
            OverrideHandler.coerce_value("maybe", bool)
        assert "Cannot coerce 'maybe' to bool" in str(ei.value)

    def test_parse_non_strict_missing_file_emits_warning_and_uses_cli(self, tmp_path):
        """Test that missing config file emits warning in non-strict mode and uses CLI values."""
        import io
        import sys

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            # config file path that does not exist
            missing_file = str(tmp_path / "nope.yaml")
            cfg = OverrideHandler.parse(
                SampleConfig,
                config_file=missing_file,
                cli_args=["name=test", "debug=true"],
                source_order=["file", "cli"],
                strict=False,
            )
            out = sys.stdout.getvalue()
            # In compact style default, a concise warning message is expected
            assert "Warning:" in out
            assert "not found" in out or "Failed to load config file" in out

            # CLI values should be applied
            assert cfg.name == "test"
            assert cfg.debug is True
        finally:
            sys.stdout = old_stdout


class TestFlattenToNested:
    """Test _flatten_to_nested type conflict handling."""

    def test_flatten_simple_keys(self):
        """Test simple non-dotted keys work correctly."""
        flat = {"a": "value", "b": 123}
        nested = OverrideHandler._flatten_to_nested(flat)
        assert nested == {"a": "value", "b": 123}

    def test_flatten_nested_keys(self):
        """Test dotted keys create nested structure."""
        flat = {"a.b.c": "value", "a.b.d": "value2", "x": "y"}
        nested = OverrideHandler._flatten_to_nested(flat)
        assert nested == {"a": {"b": {"c": "value", "d": "value2"}}, "x": "y"}

    def test_flatten_conflict_scalar_then_nested_raises(self):
        """Scalar followed by nested key should raise ValueError."""
        flat = {"a": "scalar", "a.b": "nested"}
        with pytest.raises(ValueError, match="is not a dict"):
            OverrideHandler._flatten_to_nested(flat)

    def test_flatten_conflict_nested_then_scalar_raises(self):
        """Nested key followed by scalar should raise ValueError."""
        flat = {"a.b": "nested", "a": "scalar"}
        with pytest.raises(ValueError, match="nested keys exist"):
            OverrideHandler._flatten_to_nested(flat)

    def test_flatten_deep_conflict_raises(self):
        """Deep path conflict should raise ValueError."""
        flat = {"a.b": "value", "a.b.c": "nested"}
        with pytest.raises(ValueError, match="is not a dict"):
            OverrideHandler._flatten_to_nested(flat)


class NestedDatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432
    username: str = "user"
    password: str = "pass"


class NestedAuthConfig(ConfigBase):
    enabled: bool = True
    secret: str = "default_secret"


class NestedAppConfig(ConfigBase):
    name: str = "app"
    database: NestedDatabaseConfig = NestedDatabaseConfig()
    auth: NestedAuthConfig = NestedAuthConfig()


class TestDoubleUnderscoreEnvVar:
    """Test double underscore (__) to dot conversion for nested env vars."""

    def test_env_double_underscore_converts_to_dot(self):
        os.environ["MYAPP_DATABASE__HOST"] = "prod.db"
        os.environ["MYAPP_DATABASE__PORT"] = "3306"
        try:
            overrides = OverrideHandler.get_env_overrides(prefix="MYAPP_")
            assert overrides["database.host"] == "prod.db"
            assert overrides["database.port"] == "3306"
        finally:
            del os.environ["MYAPP_DATABASE__HOST"]
            del os.environ["MYAPP_DATABASE__PORT"]

    def test_env_single_underscore_preserved(self):
        os.environ["MYAPP_SECRET_KEY"] = "abc123"
        try:
            overrides = OverrideHandler.get_env_overrides(prefix="MYAPP_")
            assert overrides["secret_key"] == "abc123"
        finally:
            del os.environ["MYAPP_SECRET_KEY"]

    def test_env_mixed_underscore_patterns(self):
        os.environ["MYAPP_AUTH__CLIENT_SECRET"] = "secret123"
        try:
            overrides = OverrideHandler.get_env_overrides(prefix="MYAPP_")
            assert overrides["auth.client_secret"] == "secret123"
        finally:
            del os.environ["MYAPP_AUTH__CLIENT_SECRET"]

    def test_env_triple_underscore_converts_correctly(self):
        os.environ["MYAPP_A___B"] = "value"
        try:
            overrides = OverrideHandler.get_env_overrides(prefix="MYAPP_")
            assert overrides["a._b"] == "value"
        finally:
            del os.environ["MYAPP_A___B"]

    def test_env_deep_nesting(self):
        os.environ["MYAPP_A__B__C__D"] = "deep"
        try:
            overrides = OverrideHandler.get_env_overrides(prefix="MYAPP_")
            assert overrides["a.b.c.d"] == "deep"
        finally:
            del os.environ["MYAPP_A__B__C__D"]


class TestDeepMerge:
    """Test _deep_merge functionality."""

    def test_deep_merge_simple(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = OverrideHandler._deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested(self):
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"y": 20, "z": 30}}
        result = OverrideHandler._deep_merge(base, override)
        assert result == {"a": {"x": 1, "y": 20, "z": 30}, "b": 3}

    def test_deep_merge_override_replaces_non_dict(self):
        base = {"a": {"x": 1}}
        override = {"a": "scalar"}
        result = OverrideHandler._deep_merge(base, override)
        assert result == {"a": "scalar"}

    def test_deep_merge_nested_replaces_scalar(self):
        base = {"a": "scalar"}
        override = {"a": {"x": 1}}
        result = OverrideHandler._deep_merge(base, override)
        assert result == {"a": {"x": 1}}


class TestFileEnvMergeIntegration:
    """Test merging file config (nested) with env config (flat) - the bug fix."""

    def test_file_and_env_merge_no_conflict(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: myapp
database:
  host: localhost
  port: 5432
auth:
  enabled: true
""")
        os.environ["TEST_DATABASE__PASSWORD"] = "secret123"
        os.environ["TEST_AUTH__SECRET"] = "my_secret"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=[],
                env_prefix="TEST_",
                source_order=["file", "env"],
            )
            assert config.name == "myapp"
            assert config.database.host == "localhost"
            assert config.database.port == 5432
            assert config.database.password == "secret123"
            assert config.auth.enabled is True
            assert config.auth.secret == "my_secret"
        finally:
            del os.environ["TEST_DATABASE__PASSWORD"]
            del os.environ["TEST_AUTH__SECRET"]

    def test_env_overrides_file_values(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: myapp
database:
  host: localhost
  port: 5432
""")
        os.environ["TEST_DATABASE__HOST"] = "prod.db"
        os.environ["TEST_DATABASE__PORT"] = "3306"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=[],
                env_prefix="TEST_",
                source_order=["env", "file"],
            )
            assert config.database.host == "prod.db"
            assert config.database.port == 3306
        finally:
            del os.environ["TEST_DATABASE__HOST"]
            del os.environ["TEST_DATABASE__PORT"]

    def test_file_overrides_env_values(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: myapp
database:
  host: file.db
  port: 5432
""")
        os.environ["TEST_DATABASE__HOST"] = "env.db"
        os.environ["TEST_DATABASE__PORT"] = "3306"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=[],
                env_prefix="TEST_",
                source_order=["file", "env"],
            )
            assert config.database.host == "file.db"
            assert config.database.port == 5432
        finally:
            del os.environ["TEST_DATABASE__HOST"]
            del os.environ["TEST_DATABASE__PORT"]

    def test_cli_overrides_env_and_file(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: myapp
database:
  host: localhost
  port: 5432
""")
        os.environ["TEST_DATABASE__HOST"] = "env.db"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=["database.host=cli.db"],
                env_prefix="TEST_",
                source_order=["cli", "env", "file"],
            )
            assert config.database.host == "cli.db"
        finally:
            del os.environ["TEST_DATABASE__HOST"]

    def test_source_order_file_env_priority(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
database:
  host: file.db
""")
        os.environ["TEST_DATABASE__HOST"] = "env.db"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=[],
                env_prefix="TEST_",
                source_order=["file", "env"],
            )
            assert config.database.host == "file.db"
        finally:
            del os.environ["TEST_DATABASE__HOST"]

    def test_source_order_env_file_priority(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
database:
  host: file.db
""")
        os.environ["TEST_DATABASE__HOST"] = "env.db"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=[],
                env_prefix="TEST_",
                source_order=["env", "file"],
            )
            assert config.database.host == "env.db"
        finally:
            del os.environ["TEST_DATABASE__HOST"]

    def test_multiple_nested_sections_merge(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: myapp
database:
  host: localhost
  username: admin
auth:
  enabled: false
""")
        os.environ["TEST_DATABASE__PORT"] = "3306"
        os.environ["TEST_DATABASE__PASSWORD"] = "secret"
        os.environ["TEST_AUTH__ENABLED"] = "true"
        os.environ["TEST_AUTH__SECRET"] = "jwt_secret"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=[],
                env_prefix="TEST_",
                source_order=["file", "env"],
            )
            assert config.name == "myapp"
            assert config.database.host == "localhost"
            assert config.database.port == 3306
            assert config.database.username == "admin"
            assert config.database.password == "secret"
            assert config.auth.enabled is False
            assert config.auth.secret == "jwt_secret"
        finally:
            del os.environ["TEST_DATABASE__PORT"]
            del os.environ["TEST_DATABASE__PASSWORD"]
            del os.environ["TEST_AUTH__ENABLED"]
            del os.environ["TEST_AUTH__SECRET"]

    def test_env_only_no_file(self):
        os.environ["TEST_NAME"] = "envapp"
        os.environ["TEST_DATABASE__HOST"] = "env.db"
        os.environ["TEST_DATABASE__PORT"] = "5433"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=None,
                cli_args=[],
                env_prefix="TEST_",
                source_order=["env"],
            )
            assert config.name == "envapp"
            assert config.database.host == "env.db"
            assert config.database.port == 5433
        finally:
            del os.environ["TEST_NAME"]
            del os.environ["TEST_DATABASE__HOST"]
            del os.environ["TEST_DATABASE__PORT"]

    def test_all_three_sources_merge(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: fileapp
database:
  host: file.db
  port: 5432
  username: file_user
  password: file_pass
auth:
  enabled: false
  secret: file_secret
""")
        os.environ["TEST_DATABASE__HOST"] = "env.db"
        os.environ["TEST_AUTH__ENABLED"] = "true"
        try:
            config = OverrideHandler.parse(
                NestedAppConfig,
                config_file=str(config_file),
                cli_args=["database.port=9999", "auth.secret=cli_secret"],
                env_prefix="TEST_",
                source_order=["cli", "env", "file"],
            )
            assert config.name == "fileapp"
            assert config.database.host == "env.db"
            assert config.database.port == 9999
            assert config.database.username == "file_user"
            assert config.database.password == "file_pass"
            assert config.auth.enabled is True
            assert config.auth.secret == "cli_secret"
        finally:
            del os.environ["TEST_DATABASE__HOST"]
            del os.environ["TEST_AUTH__ENABLED"]
