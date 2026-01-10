"""confee - Configuration Enhanced & Easy ☕️

A Hydra-like configuration parser helper package with Pydantic support.

Features:
- Type-safe configuration with Pydantic V2
- Multi-format support: YAML, JSON, TOML
- Flexible override system: CLI args + environment variables
- Configuration inheritance with defaults
- File references: @file: and @config: prefixes
- Secret field masking
- Configuration freezing (immutability)
- JSON Schema generation
- Async loading support
- Plugin system for custom formats

Examples:
    >>> from confee import ConfigBase, SecretField
    >>>
    >>> class AppConfig(ConfigBase):
    ...     name: str
    ...     debug: bool = False
    ...     api_key: str = SecretField(description="API key")
    ...
    >>> # Load from multiple sources
    >>> config = AppConfig.load(config_file="config.yaml")
    >>>
    >>> # Generate JSON Schema
    >>> config.save_schema("schema.json")
"""

__version__ = "0.3.0"
__author__ = "JunSeok Kim <infend@gmail.com>"
__license__ = "MIT"

# Core classes
from .config import ConfigBase, SecretField
from .loaders import ConfigLoader, load_config, load_from_file
from .parser import ConfigParser

# Override handling (kept for backward compatibility)
from .overrides import OverrideHandler, is_help_command

# New modular components
from .colors import Color, ProgressIndicator
from .error_formatter import ErrorFormatter, FieldErrorDetail
from .help_formatter import HelpFormatter

# Schema generation
from .schema import SchemaGenerator, SchemaValidator

# Plugin system
from .plugins import (
    LoaderPlugin,
    PluginRegistry,
    SourcePlugin,
)

# Async support
from .async_loader import (
    AsyncConfigLoader,
    ConfigMerger,
    ConfigWatcher,
)

__all__ = [
    # Core
    "ConfigBase",
    "SecretField",
    "ConfigLoader",
    "ConfigParser",
    "load_config",
    "load_from_file",
    # Override handling
    "OverrideHandler",
    "HelpFormatter",
    "ErrorFormatter",
    "FieldErrorDetail",
    "is_help_command",
    # Colors and UI
    "Color",
    "ProgressIndicator",
    # Schema
    "SchemaGenerator",
    "SchemaValidator",
    # Plugins
    "PluginRegistry",
    "LoaderPlugin",
    "SourcePlugin",
    # Async
    "AsyncConfigLoader",
    "ConfigWatcher",
    "ConfigMerger",
]
