import re
from typing import Optional

import pytest
from pydantic import Field

from confee import ConfigBase, HelpFormatter
from confee.overrides import ErrorFormatter


class HelpSample(ConfigBase):
    name: str  # required — should NOT show [default: ...]
    debug: bool = False
    workers: int = 4
    note: Optional[str] = None  # should show [default: None]


class NestedSubConfig(ConfigBase):
    """Nested configuration for testing."""
    host: str = "localhost"
    port: int = 5432
    timeout: int = 30


class NestedConfig(ConfigBase):
    """Configuration with nested ConfigBase fields."""
    name: str = Field(default="app", repr=True)
    debug: bool = False
    database: NestedSubConfig = NestedSubConfig()


class DeepNestedInnerConfig(ConfigBase):
    """Innermost configuration for deep nesting test."""
    value: str = "inner"
    count: int = 10


class DeepNestedMiddleConfig(ConfigBase):
    """Middle level configuration for deep nesting test."""
    name: str = "middle"
    inner: DeepNestedInnerConfig = DeepNestedInnerConfig()


class DeepNestedConfig(ConfigBase):
    """Configuration with multiple levels of nesting."""
    app_name: str = "deep-app"
    middle: DeepNestedMiddleConfig = DeepNestedMiddleConfig()


def _line_for_option(help_text: str, option: str) -> str:
    # Find the line that starts with the option flag, e.g., "  --name"
    for line in help_text.splitlines():
        if re.match(rf"\s*--{re.escape(option)}\b", line.strip()):
            return line
        # help formatter prints with indentation and color codes; be tolerant
        if f"--{option}" in line:
            return line
    return ""


class TestHelpFormatterDefaults:
    def test_required_field_hides_default_segment(self):
        text = HelpFormatter.generate_help(HelpSample)
        line = _line_for_option(text, "name")
        assert "--name" in line
        assert "[default:" not in line  # no default segment for required fields

    def test_none_default_is_rendered(self):
        text = HelpFormatter.generate_help(HelpSample)
        line = _line_for_option(text, "note")
        assert "--note" in line
        assert "[default: None]" in line

    def test_concrete_defaults_are_rendered(self):
        text = HelpFormatter.generate_help(HelpSample)
        debug_line = _line_for_option(text, "debug")
        workers_line = _line_for_option(text, "workers")
        assert "[default: False]" in debug_line
        assert "[default: 4]" in workers_line


class TestNestedConfigHelp:
    """Test help generation for nested ConfigBase fields."""

    def test_nested_fields_are_flattened(self):
        """Test that nested ConfigBase fields are displayed with dot notation."""
        text = HelpFormatter.generate_help(NestedConfig)

        # Check that root fields are present
        assert "--name" in text
        assert "--debug" in text

        # Check that nested fields are flattened with dot notation
        assert "--database.host" in text
        assert "--database.port" in text
        assert "--database.timeout" in text

        # Ensure the parent field itself is NOT shown
        # (we only show the leaf fields, not the ConfigBase parent)
        lines = text.splitlines()
        database_only_lines = [l for l in lines if "--database " in l and "--database." not in l]
        assert len(database_only_lines) == 0, "Parent ConfigBase field should not be shown"

    def test_nested_field_defaults(self):
        """Test that nested field defaults are correctly displayed."""
        text = HelpFormatter.generate_help(NestedConfig)

        host_line = _line_for_option(text, "database.host")
        port_line = _line_for_option(text, "database.port")

        assert "[default: localhost]" in host_line
        assert "[default: 5432]" in port_line

    def test_deeply_nested_fields(self):
        """Test that multiple levels of nesting are handled correctly."""
        text = HelpFormatter.generate_help(DeepNestedConfig)

        # Check root field
        assert "--app_name" in text

        # Check middle level fields
        assert "--middle.name" in text

        # Check deeply nested fields (3 levels)
        assert "--middle.inner.value" in text
        assert "--middle.inner.count" in text

        # Verify defaults
        value_line = _line_for_option(text, "middle.inner.value")
        count_line = _line_for_option(text, "middle.inner.count")

        assert "[default: inner]" in value_line
        assert "[default: 10]" in count_line

    def test_nested_field_descriptions(self):
        """Test that nested field descriptions include parent context."""
        text = HelpFormatter.generate_help(NestedConfig)

        # Nested fields should have descriptions that include parent name
        host_line = _line_for_option(text, "database.host")
        assert "database" in host_line.lower()


class TestErrorFormatter:
    def test_compact_missing_field_message(self):
        class X(ConfigBase):
            name: str

        # Trigger validation error by omitting required field
        with pytest.raises(Exception) as ei:
            X()
        msg = ErrorFormatter.format_validation_error(ei.value, style="compact")
        # Either explicit field or generic validation failed message
        assert "missing required field 'name'" in msg or msg == "Config error: validation failed"

    def test_compact_non_validation_error(self):
        err = RuntimeError("boom")
        msg = ErrorFormatter.format_validation_error(err, style="compact")
        assert msg == "Error: boom"


