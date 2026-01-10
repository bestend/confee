"""JSON Schema generation and validation utilities."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from .config import ConfigBase


class SchemaGenerator:
    """Generate JSON Schema from ConfigBase classes.

    Supports exporting schemas in JSON Schema Draft 2020-12 format,
    compatible with IDE autocomplete and validation tools.

    Examples:
        >>> class AppConfig(ConfigBase):
        ...     name: str
        ...     debug: bool = False
        ...
        >>> schema = SchemaGenerator.generate(AppConfig)
        >>> SchemaGenerator.save(AppConfig, "schema.json")
    """

    @staticmethod
    def generate(
        config_class: Type[ConfigBase],
        title: Optional[str] = None,
        description: Optional[str] = None,
        include_defaults: bool = True,
    ) -> Dict[str, Any]:
        """Generate JSON Schema from a ConfigBase class.

        Args:
            config_class: Configuration class to generate schema for
            title: Optional schema title (defaults to class name)
            description: Optional schema description (defaults to class docstring)
            include_defaults: Whether to include default values in schema
                (currently reserved for future implementation)

        Returns:
            JSON Schema dictionary

        Examples:
            >>> schema = SchemaGenerator.generate(AppConfig)
            >>> print(json.dumps(schema, indent=2))
        """
        # TODO: Implement include_defaults parameter to optionally strip default
        # values from the generated schema. Pydantic's model_json_schema() always
        # includes defaults; post-processing would be needed to remove them.
        _ = include_defaults  # Reserved for future implementation

        # Use Pydantic's built-in schema generation
        schema = config_class.model_json_schema()

        # Override title if provided
        if title:
            schema["title"] = title

        # Override description if provided
        if description:
            schema["description"] = description
        elif config_class.__doc__ and "description" not in schema:
            schema["description"] = config_class.__doc__.strip()

        # Add $schema for validation
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"

        # Add confee-specific metadata
        schema["x-confee-version"] = "0.3.0"

        return schema

    @staticmethod
    def save(
        config_class: Type[ConfigBase],
        file_path: Union[str, Path],
        title: Optional[str] = None,
        description: Optional[str] = None,
        indent: int = 2,
    ) -> None:
        """Save JSON Schema to a file.

        Args:
            config_class: Configuration class to generate schema for
            file_path: Output file path
            title: Optional schema title
            description: Optional schema description
            indent: JSON indentation level

        Examples:
            >>> SchemaGenerator.save(AppConfig, "config-schema.json")
        """
        schema = SchemaGenerator.generate(config_class, title, description)
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def to_yaml_header(
        config_class: Type[ConfigBase],
        schema_path: str = "schema.json",
    ) -> str:
        """Generate YAML header comment with schema reference.

        Args:
            config_class: Configuration class
            schema_path: Relative path to schema file

        Returns:
            YAML comment string with schema reference

        Examples:
            >>> header = SchemaGenerator.to_yaml_header(AppConfig, "./schema.json")
            >>> print(header)
            # yaml-language-server: $schema=./schema.json
            # vim: set filetype=yaml.confee:
        """
        lines = [
            f"# yaml-language-server: $schema={schema_path}",
            "# vim: set filetype=yaml.confee:",
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_example_config(
        config_class: Type[ConfigBase],
        output_format: str = "yaml",
        include_comments: bool = True,
    ) -> str:
        """Generate an example configuration file from schema.

        Args:
            config_class: Configuration class
            output_format: Output format ("yaml" or "json")
            include_comments: Whether to include field descriptions as comments

        Returns:
            Example configuration string

        Examples:
            >>> example = SchemaGenerator.generate_example_config(AppConfig)
            >>> print(example)
        """
        import yaml

        schema = SchemaGenerator.generate(config_class)
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        if output_format == "json":
            example = {}
            for name, prop in properties.items():
                example[name] = prop.get("default", _get_example_value(prop))
            return json.dumps(example, indent=2, ensure_ascii=False)

        # YAML format with optional comments
        lines = []

        if include_comments:
            lines.append(f"# Example configuration for {config_class.__name__}")
            lines.append("")

        for name, prop in properties.items():
            if include_comments and "description" in prop:
                lines.append(f"# {prop['description']}")

            default = prop.get("default")
            value = default if default is not None else _get_example_value(prop)

            # Mark required fields
            req_marker = " # required" if name in required and include_comments else ""

            # Format the value
            if isinstance(value, bool):
                yaml_value = "true" if value else "false"
            elif isinstance(value, str):
                yaml_value = f'"{value}"' if " " in value or not value else value
            elif value is None:
                yaml_value = "null"
            elif isinstance(value, (dict, list)):
                yaml_value = yaml.dump(value, default_flow_style=True).strip()
            else:
                yaml_value = str(value)

            lines.append(f"{name}: {yaml_value}{req_marker}")

            if include_comments:
                lines.append("")

        return "\n".join(lines)


def _get_example_value(prop: Dict[str, Any]) -> Any:
    """Get an example value for a JSON Schema property.

    Args:
        prop: JSON Schema property definition

    Returns:
        Example value based on type
    """
    prop_type = prop.get("type", "string")

    # Check for examples
    if "examples" in prop and prop["examples"]:
        return prop["examples"][0]

    # Check for enum
    if "enum" in prop:
        return prop["enum"][0]

    # Type-based defaults
    type_examples = {
        "string": "example",
        "integer": 0,
        "number": 0.0,
        "boolean": False,
        "array": [],
        "object": {},
        "null": None,
    }

    if isinstance(prop_type, list):
        # Union type - use first non-null type
        for t in prop_type:
            if t != "null":
                return type_examples.get(t, "")
        return None

    return type_examples.get(prop_type, "")


class SchemaValidator:
    """Validate configuration data against JSON Schema.

    Uses jsonschema library for validation if available,
    falls back to Pydantic validation otherwise.

    Examples:
        >>> validator = SchemaValidator(AppConfig)
        >>> errors = validator.validate({"name": "app", "debug": "not-a-bool"})
        >>> if errors:
        ...     print("Validation failed:", errors)
    """

    def __init__(self, config_class: Type[ConfigBase]):
        """Initialize validator.

        Args:
            config_class: Configuration class to validate against
        """
        self.config_class = config_class
        self.schema = SchemaGenerator.generate(config_class)

    def validate(self, data: Dict[str, Any]) -> list:
        """Validate data against schema.

        Args:
            data: Configuration data to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        try:
            # Try jsonschema if available
            import jsonschema

            validator = jsonschema.Draft202012Validator(self.schema)
            errors = list(validator.iter_errors(data))
            return [f"{e.json_path}: {e.message}" for e in errors]
        except ImportError:
            # Fall back to Pydantic validation
            try:
                self.config_class(**data)
                return []
            except Exception as e:
                return [str(e)]

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """Check if data is valid.

        Args:
            data: Configuration data to validate

        Returns:
            True if valid, False otherwise
        """
        return len(self.validate(data)) == 0
