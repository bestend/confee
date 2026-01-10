# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-01-10

### Added
- **🗂️ TOML Support** — Native TOML file loading with `tomllib` (Python 3.11+) / `tomli` (Python 3.9-3.10)
  - `ConfigLoader.load_toml()` for TOML files
  - `ConfigLoader.load_pyproject()` for pyproject.toml [tool.xxx] sections
- **🔌 Plugin System** — Extensible loader architecture for custom formats
  - `@PluginRegistry.loader(".ext")` decorator for custom format loaders
  - `@PluginRegistry.source("name")` decorator for custom data sources
- **🔐 Secret Field Masking** — Protect sensitive configuration values
  - `SecretField()` function to mark fields as sensitive
  - `to_safe_dict()` / `to_safe_json()` methods to mask secrets in output
- **🧊 Config Freezing** — Immutable configuration support
  - `freeze()` / `unfreeze()` methods for runtime immutability
  - `is_frozen()` to check frozen state
  - `copy_unfrozen()` to create mutable copies
- **📐 JSON Schema Export** — Generate JSON Schema from config classes
  - `SchemaGenerator` class for schema generation
  - `SchemaValidator` for schema-based validation
  - `to_json_schema()` / `save_schema()` methods on ConfigBase
- **⚡ Async Config Loading** — Non-blocking configuration loading
  - `AsyncConfigLoader` with async/await support
  - `load_remote()` for loading configs from URLs (requires `aiohttp`)
  - `ConfigWatcher` for file change monitoring
  - `ConfigMerger` for deep configuration merging
- **🔄 Config Diff & Merge** — Compare and combine configurations
  - `diff()` method to compare two configurations
  - `merge()` method to combine configurations

### Changed
- **📦 Modular Architecture** — Split monolithic modules into focused components
  - `colors.py` — ANSI color utilities with `Color` class and `ProgressIndicator`
  - `error_formatter.py` — User-friendly validation error formatting
  - `help_formatter.py` — Typer-style help generation and markdown docs
  - `plugins.py` — Plugin registry system
  - `schema.py` — JSON Schema generation utilities
  - `async_loader.py` — Async loading and file watching
- Improved `ConfigBase.print()` with `safe=True` option for secret masking

### Dependencies
- Added `tomli>=2.0.0` for Python < 3.11 (TOML support)
- Added optional `aiohttp>=3.8.0` for remote config loading (`pip install confee[remote]`)

---

## [0.2.2] - 2026-01-02

### Improved
- Help display now groups nested config fields by section with `[section] Options:` headers
- Improved readability for hierarchical configuration structures in `--help` output

---

## [0.2.0] - 2025-12-23

### Added
- Better error messages with detailed validation feedback
- Support for more flexible CLI argument parsing
- Enhanced configuration merging capabilities

### Changed
- Improved type checking and validation error reporting
- Better handling of optional configuration fields
- More robust file loading and error handling

### Fixed
- Fixed type hints for configuration file paths
- Improved YAML/JSON parsing consistency

---

## [0.1.4] - 2025-12-21

### Improved
- Upgraded minimum Python version to 3.9+ for better stability
- Enhanced error handling for missing configuration files
- Improved code quality and type safety

---

## [0.1.2] - 2025-12-21

### Added
- Type-safe configuration with Pydantic V2
- Multi-source configuration (file/env/CLI)
- Nested field access with dot notation
- File reference support (@file:, @config:)
- Configuration inheritance with override_with()
- Strict/non-strict validation modes
- Auto help generation with --help flag
- Bilingual documentation (English & Korean)

### Features
- YAML/JSON auto-detection
- Environment variable override with custom prefix
- CLI argument parsing with flexible syntax
- Nested configuration support
- Color-coded terminal output
- Comprehensive error messages


---

## Format

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

Versions follow [Semantic Versioning](https://semver.org/) (Major.Minor.Patch).

