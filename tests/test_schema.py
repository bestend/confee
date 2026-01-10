"""Tests for schema module."""

from __future__ import annotations

import json
from pathlib import Path

from confee import ConfigBase


class TestSchemaGenerator:
    def test_generate_basic_schema(self) -> None:
        from confee.schema import SchemaGenerator

        class SimpleConfig(ConfigBase):
            name: str
            count: int = 0

        schema = SchemaGenerator.generate(SimpleConfig)

        assert "$schema" in schema
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "x-confee-version" in schema
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "count" in schema["properties"]

    def test_generate_with_custom_title(self) -> None:
        from confee.schema import SchemaGenerator

        class MyConfig(ConfigBase):
            value: str

        schema = SchemaGenerator.generate(MyConfig, title="Custom Title")

        assert schema["title"] == "Custom Title"

    def test_generate_with_custom_description(self) -> None:
        from confee.schema import SchemaGenerator

        class MyConfig(ConfigBase):
            value: str

        schema = SchemaGenerator.generate(MyConfig, description="Custom desc")

        assert schema["description"] == "Custom desc"

    def test_generate_uses_docstring_as_description(self) -> None:
        from confee.schema import SchemaGenerator

        class DocConfig(ConfigBase):
            """This is the config description."""

            value: str

        schema = SchemaGenerator.generate(DocConfig)

        assert schema["description"] == "This is the config description."

    def test_save_creates_file(self, tmp_path: Path) -> None:
        from confee.schema import SchemaGenerator

        class SaveConfig(ConfigBase):
            name: str

        output_path = tmp_path / "schema.json"
        SchemaGenerator.save(SaveConfig, output_path)

        assert output_path.exists()

        with open(output_path) as f:
            saved_schema = json.load(f)

        assert "properties" in saved_schema
        assert "name" in saved_schema["properties"]

    def test_save_creates_parent_directories(self, tmp_path: Path) -> None:
        from confee.schema import SchemaGenerator

        class SaveConfig(ConfigBase):
            name: str

        output_path = tmp_path / "nested" / "dir" / "schema.json"
        SchemaGenerator.save(SaveConfig, output_path)

        assert output_path.exists()

    def test_to_yaml_header(self) -> None:
        from confee.schema import SchemaGenerator

        class MyConfig(ConfigBase):
            name: str

        header = SchemaGenerator.to_yaml_header(MyConfig, "./config-schema.json")

        assert "yaml-language-server" in header
        assert "$schema=./config-schema.json" in header
        assert "vim:" in header

    def test_generate_example_config_yaml(self) -> None:
        from confee.schema import SchemaGenerator

        class ExampleConfig(ConfigBase):
            name: str
            debug: bool = False
            count: int = 10

        example = SchemaGenerator.generate_example_config(
            ExampleConfig, output_format="yaml", include_comments=True
        )

        assert "name:" in example
        assert "debug:" in example
        assert "count:" in example
        assert "# required" in example or "name:" in example

    def test_generate_example_config_json(self) -> None:
        from confee.schema import SchemaGenerator

        class ExampleConfig(ConfigBase):
            name: str
            debug: bool = False

        example = SchemaGenerator.generate_example_config(ExampleConfig, output_format="json")

        data = json.loads(example)
        assert "name" in data
        assert "debug" in data
        assert data["debug"] is False

    def test_generate_example_config_without_comments(self) -> None:
        from confee.schema import SchemaGenerator

        class ExampleConfig(ConfigBase):
            name: str

        example = SchemaGenerator.generate_example_config(
            ExampleConfig, output_format="yaml", include_comments=False
        )

        assert "# Example" not in example
        assert "# required" not in example


class TestSchemaValidator:
    def test_validate_valid_data(self) -> None:
        from confee.schema import SchemaValidator

        class ValidConfig(ConfigBase):
            name: str
            count: int = 0

        validator = SchemaValidator(ValidConfig)
        errors = validator.validate({"name": "test", "count": 5})

        assert errors == []

    def test_validate_invalid_data(self) -> None:
        from confee.schema import SchemaValidator

        class ValidConfig(ConfigBase):
            name: str
            count: int = 0

        validator = SchemaValidator(ValidConfig)
        errors = validator.validate({"count": "not-an-int"})

        assert len(errors) > 0

    def test_is_valid_returns_bool(self) -> None:
        from confee.schema import SchemaValidator

        class ValidConfig(ConfigBase):
            name: str

        validator = SchemaValidator(ValidConfig)

        assert validator.is_valid({"name": "test"}) is True
        assert validator.is_valid({}) is False


class TestGetExampleValue:
    def test_example_from_examples_field(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "string", "examples": ["my-example"]}
        assert _get_example_value(prop) == "my-example"

    def test_example_from_enum(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "string", "enum": ["a", "b", "c"]}
        assert _get_example_value(prop) == "a"

    def test_example_string_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "string"}
        assert _get_example_value(prop) == "example"

    def test_example_integer_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "integer"}
        assert _get_example_value(prop) == 0

    def test_example_number_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "number"}
        assert _get_example_value(prop) == 0.0

    def test_example_boolean_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "boolean"}
        assert _get_example_value(prop) is False

    def test_example_array_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "array"}
        assert _get_example_value(prop) == []

    def test_example_object_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "object"}
        assert _get_example_value(prop) == {}

    def test_example_null_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "null"}
        assert _get_example_value(prop) is None

    def test_example_union_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": ["string", "null"]}
        assert _get_example_value(prop) == "example"

    def test_example_union_type_null_first(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": ["null", "integer"]}
        assert _get_example_value(prop) == 0

    def test_example_union_type_only_null(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": ["null"]}
        assert _get_example_value(prop) is None

    def test_example_unknown_type(self) -> None:
        from confee.schema import _get_example_value

        prop = {"type": "unknown"}
        assert _get_example_value(prop) == ""
