"""Configuration base classes with Pydantic validation and inheritance support."""

from pathlib import Path
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional, Set, Type, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound="ConfigBase")


def SecretField(
    default: Any = ...,
    *,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Create a field that will be masked in output.

    Secret fields are automatically masked when using print() or to_safe_dict().

    Args:
        default: Default value for the field
        description: Field description
        **kwargs: Additional Pydantic Field arguments

    Returns:
        Pydantic Field with secret metadata

    Note:
        SecretField only masks values when using ``to_safe_dict()``, ``to_safe_json()``,
        or ``print(safe=True)``. Direct attribute access (e.g., ``config.password``)
        and standard serialization methods like ``model_dump()`` or ``to_dict()``
        will still expose the actual values. Always use safe methods when logging
        or displaying configuration.

    Examples:
        >>> class DbConfig(ConfigBase):
        ...     host: str
        ...     password: str = SecretField(description="Database password")
        ...
        >>> config = DbConfig(host="localhost", password="secret123")
        >>> config.to_safe_dict()
        {'host': 'localhost', 'password': '***MASKED***'}
    """
    json_schema_extra = kwargs.pop("json_schema_extra", {})
    json_schema_extra["x-secret"] = True

    return Field(
        default,
        description=description,
        json_schema_extra=json_schema_extra,
        **kwargs,
    )


class ConfigBase(BaseModel):
    """Base configuration class using Pydantic for type validation.

    Supports:
    - Type checking and validation
    - Configuration inheritance
    - Flexible field handling (strict/non-strict modes)
    - Environment variable overrides
    - Secret field masking
    - Configuration freezing (immutability)

    Examples:
        >>> class AppConfig(ConfigBase):
        ...     name: str
        ...     debug: bool = False
        ...     workers: int = 4

        >>> config = AppConfig(name="myapp")
        >>> config.name
        'myapp'

        >>> # Secret fields are masked in output
        >>> class DbConfig(ConfigBase):
        ...     host: str
        ...     password: str = SecretField()
        ...
        >>> config = DbConfig(host="localhost", password="secret")
        >>> config.to_safe_dict()["password"]
        '***MASKED***'
    """

    model_config = ConfigDict(
        extra="ignore",  # Default: ignore extra fields (strict=False)
        validate_default=True,
        str_strip_whitespace=True,
    )

    # Class-level frozen state tracking
    _frozen_instances: ClassVar[Set[int]] = set()

    def __del__(self) -> None:
        """Ensure frozen state is cleaned up when the instance is garbage-collected."""
        instance_id = id(self)
        self._frozen_instances.discard(instance_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """Convert configuration to JSON string."""
        return self.model_dump_json(**kwargs)

    def to_safe_dict(self, mask: str = "***MASKED***") -> Dict[str, Any]:
        """Convert configuration to dictionary with secret fields masked.

        Args:
            mask: String to use for masking secret values

        Returns:
            Dictionary with secret fields masked

        Examples:
            >>> config = DbConfig(host="localhost", password="secret123")
            >>> config.to_safe_dict()
            {'host': 'localhost', 'password': '***MASKED***'}
        """
        data = self.model_dump()
        secret_fields = self._get_secret_fields()

        def mask_secrets(obj: Any, path: str = "") -> Any:
            if isinstance(obj, dict):
                return {k: mask_secrets(v, f"{path}.{k}" if path else k) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [mask_secrets(item, path) for item in obj]
            elif path in secret_fields:
                return mask
            return obj

        return mask_secrets(data)

    def to_safe_json(self, mask: str = "***MASKED***", **kwargs: Any) -> str:
        """Convert configuration to JSON string with secret fields masked.

        Args:
            mask: String to use for masking secret values
            **kwargs: Additional json.dumps arguments

        Returns:
            JSON string with secret fields masked
        """
        import json

        return json.dumps(self.to_safe_dict(mask), **kwargs)

    @classmethod
    def _get_secret_fields(cls) -> FrozenSet[str]:
        """Get set of secret field names (including nested paths).

        This method inspects the model's fields for the ``x-secret`` marker set
        by :func:`SecretField` and also recursively traverses any nested
        :class:`ConfigBase` subclasses to build dot-separated paths for nested
        secret fields.
        """
        secret_fields: Set[str] = set()

        for name, field in cls.model_fields.items():
            # Direct secret field on this model
            json_extra = field.json_schema_extra
            if isinstance(json_extra, dict) and json_extra.get("x-secret"):
                secret_fields.add(name)

            # Nested ConfigBase field: collect its secret fields with prefix
            field_type = field.annotation
            try:
                if isinstance(field_type, type) and issubclass(field_type, ConfigBase):
                    for nested_secret in field_type._get_secret_fields():
                        secret_fields.add(f"{name}.{nested_secret}")
            except TypeError:
                # field.annotation may not be a type (e.g. typing constructs); ignore
                pass

        return frozenset(secret_fields)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create configuration from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create configuration from JSON string."""
        return cls.model_validate_json(json_str)

    def print(self, safe: bool = True) -> None:
        """Print the configuration instance using devtools.debug.

        Args:
            safe: If True, mask secret fields in output (default: True)
        """
        from devtools import debug

        if safe:
            # Print with secrets masked
            debug(self.to_safe_dict(), color=True)
        else:
            debug(self, color=True)

    def freeze(self: T) -> T:
        """Make this configuration instance immutable.

        After freezing, any attempt to modify fields will raise an error.
        Returns self for method chaining.

        Returns:
            Self (for method chaining)

        Examples:
            >>> config = AppConfig(name="myapp").freeze()
            >>> config.name = "other"  # Raises AttributeError
        """
        ConfigBase._frozen_instances.add(id(self))
        return self

    def unfreeze(self: T) -> T:
        """Make this configuration instance mutable again.

        Returns:
            Self (for method chaining)
        """
        ConfigBase._frozen_instances.discard(id(self))
        return self

    def is_frozen(self) -> bool:
        """Check if this instance is frozen.

        Returns:
            True if frozen, False otherwise
        """
        return id(self) in ConfigBase._frozen_instances

    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to enforce frozen state."""
        if hasattr(self, "__dict__") and id(self) in ConfigBase._frozen_instances:
            raise AttributeError(
                f"Cannot modify frozen configuration. Call .unfreeze() first to make it mutable."
            )
        super().__setattr__(name, value)

    def copy_unfrozen(self: T) -> T:
        """Create a mutable copy of this configuration.

        Returns:
            New unfrozen configuration instance with same values
        """
        return self.__class__(**self.model_dump())

    @classmethod
    def load(
        cls: Type[T],
        config_file: Optional[Union[str, Path]] = None,
        cli_args: Optional[List[str]] = None,
        env_prefix: str = "CONFEE_",
        source_order: Optional[List[str]] = None,
        help_flags: Optional[List[str]] = None,
        strict: bool = True,
    ) -> T:
        """Load configuration from multiple sources (file, environment, CLI).

        Unified parsing method — processes file, environment variables, and CLI at once.
        This consolidates the capabilities of OverrideHandler.parse() and load_from_file().

        Args:
            config_file: Path to configuration file (YAML/JSON)
            cli_args: CLI arguments list (default: sys.argv[1:])
            env_prefix: Environment variable prefix (default: "CONFEE_")
            source_order: Parsing order (default: ["cli", "env", "file"])
            help_flags: Help flags (default: ["--help", "-h"])
            strict: If True, forbid extra fields; if False, ignore extra fields (default: True)

        Returns:
            Configuration instance

        Examples:
            >>> # Automatically parse from all sources
            >>> config = AppConfig.load(config_file="config.yaml")

            >>> # Use file only
            >>> config = AppConfig.load(
            ...     config_file="config.yaml",
            ...     source_order=["file"]
            ... )

            >>> # Use CLI + environment variables only
            >>> config = AppConfig.load(source_order=["cli", "env"])
        """
        from .overrides import OverrideHandler

        # Convert Path to str for type compatibility
        config_file_str: Optional[str] = None
        if config_file is not None:
            config_file_str = str(config_file)

        try:
            config = OverrideHandler.parse(
                cls,
                config_file=config_file_str,
                cli_args=cli_args,
                env_prefix=env_prefix,
                source_order=source_order,
                help_flags=help_flags,
                strict=strict,
            )
            config.print()
            return config
        except FileNotFoundError:
            import sys
            from pathlib import Path

            if config_file is not None:
                abs_path = Path(config_file).resolve()
                print("Error: Config file not found", file=sys.stderr)
                print(f"  File: {config_file}", file=sys.stderr)
                print(f"  Full path: {abs_path}", file=sys.stderr)
            else:
                print("Error: Config file not found", file=sys.stderr)
            print(f"  Current directory: {Path.cwd()}", file=sys.stderr)
            raise SystemExit(1)

    def override_with(self: T, defaults: "ConfigBase") -> T:
        """Override this configuration's values with defaults from another configuration.
        This configuration's values take precedence over the defaults.

        Args:
            defaults: Default configuration to merge with (lower priority)

        Returns:
            Merged configuration instance

        Examples:
            >>> defaults_config = AppConfig(name="default", debug=False, workers=4)
            >>> custom_config = AppConfig(name="custom", debug=True)
            >>> result = custom_config.override_with(defaults_config)
            >>> result.name
            'custom'
            >>> result.workers
            4
        """
        defaults_dict = defaults.model_dump()
        current_dict = self.model_dump()

        # Create merged dict: start with defaults, override with non-None current values
        merged = {**defaults_dict}
        for key, value in current_dict.items():
            # Override with current value if it's not None
            if value is not None:
                merged[key] = value

        return self.__class__(**merged)

    @classmethod
    def set_strict_mode(cls, strict: bool = True) -> None:
        """Enable/disable strict mode.
        - True: forbid extra fields (forbid unknown fields)
        - False: ignore extra fields (strict=False)
        """
        if strict:
            cls.model_config = ConfigDict(**{**cls.model_config, "extra": "forbid"})
        else:
            cls.model_config = ConfigDict(**{**cls.model_config, "extra": "ignore"})

    @classmethod
    def to_json_schema(
        cls,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate JSON Schema for this configuration class.

        Args:
            title: Optional schema title (defaults to class name)
            description: Optional schema description

        Returns:
            JSON Schema dictionary

        Examples:
            >>> schema = AppConfig.to_json_schema()
            >>> with open("schema.json", "w") as f:
            ...     json.dump(schema, f, indent=2)
        """
        from .schema import SchemaGenerator

        return SchemaGenerator.generate(cls, title, description)

    @classmethod
    def save_schema(
        cls,
        file_path: Union[str, Path],
        title: Optional[str] = None,
    ) -> None:
        """Save JSON Schema to a file.

        Args:
            file_path: Output file path
            title: Optional schema title
        """
        from .schema import SchemaGenerator

        SchemaGenerator.save(cls, file_path, title)

    def diff(self, other: "ConfigBase") -> Dict[str, Any]:
        """Compare this configuration with another and return differences.

        Args:
            other: Another configuration instance to compare with

        Returns:
            Dictionary of differences: {field: (self_value, other_value)}

        Examples:
            >>> config1 = AppConfig(name="app1", debug=True)
            >>> config2 = AppConfig(name="app2", debug=True)
            >>> config1.diff(config2)
            {'name': ('app1', 'app2')}
        """
        self_dict = self.model_dump()
        other_dict = other.model_dump()

        differences: Dict[str, Any] = {}

        all_keys = set(self_dict.keys()) | set(other_dict.keys())
        for key in all_keys:
            self_val = self_dict.get(key)
            other_val = other_dict.get(key)
            if self_val != other_val:
                differences[key] = (self_val, other_val)

        return differences

    def merge(self: T, other: "ConfigBase", override: bool = True) -> T:
        """Merge another configuration into this one.

        Args:
            other: Another configuration to merge
            override: If True, other's values override self's values

        Returns:
            New merged configuration instance

        Examples:
            >>> base = AppConfig(name="app", debug=False)
            >>> override = AppConfig(name="app", debug=True, workers=8)
            >>> merged = base.merge(override)
        """
        self_dict = self.model_dump()
        other_dict = other.model_dump()

        if override:
            merged = {**self_dict, **other_dict}
        else:
            merged = {**other_dict, **self_dict}

        return self.__class__(**merged)
