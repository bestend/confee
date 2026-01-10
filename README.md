<p align="center">
  <img src="https://raw.githubusercontent.com/bestend/confee/main/assets/logo.png" width="360" />
</p>

<div align="center">

**Language:** [한국어](./README.ko.md) | English

Hydra-style Configuration Management + Pydantic Type Safety + Typer-style Auto Help Generation

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-alpha-yellow)](https://github.com/bestend/confee)
[![Tests](https://github.com/bestend/confee/actions/workflows/tests.yml/badge.svg)](https://github.com/bestend/confee/actions/workflows/tests.yml)

</div>

---

## ☕️ Overview

**confee** is a package that makes configuration management in Python applications simple, type-safe, and intuitive. It combines the best of Hydra and Pydantic, allowing you to manage configuration files, environment variables, and CLI arguments seamlessly.

---

## ✨ Key Features

- **🎯 Type-Safe Configuration** — Automatic type validation & IDE autocomplete with Pydantic V2
- **📋 Multi-Format Support** — Automatic detection and parsing of YAML, JSON, and TOML
- **🔄 Flexible Override System** — Override values via CLI arguments and environment variables
- **🏗️ Configuration Inheritance** — Merge and combine parent-child configurations
- **📁 File Reference** — Load file contents with `@file:` & `@config:` prefixes
- **🔐 Secret Masking** — Mark sensitive fields with `SecretField()` for automatic masking
- **🧊 Config Freezing** — Freeze configurations for runtime immutability
- **📐 JSON Schema Export** — Generate JSON Schema from configuration classes
- **⚡ Async Loading** — Non-blocking config loading with file watching support
- **🔌 Plugin System** — Extend with custom format loaders and data sources
- **📦 Zero Configuration** — Ready to use with sensible defaults
- **⚙️ Parse Order Control** — Freely adjust priority of file/env/cli sources
- **💬 Auto Help Generation** — Display all options and defaults with `--help` flag
- **🪆 Nested Field Access** — Override nested fields with dot notation (database.host=localhost)
- **🧾 Verbosity Control** — Adjust output verbosity with `--quiet`/`--verbose`/`--no-color` flags

---

## 📦 Installation

```bash
pip install confee

# With optional features
pip install confee[remote]  # For async remote config loading
```

---

## 🚀 Quick Start

### Basic Usage

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4

# Parse from all sources (file, environment, CLI)
config = AppConfig.load(config_file="config.yaml")

print(config.name)     # Type-safe access
print(config.debug)    # Full IDE support
print(config.workers)  # Auto-completion enabled
```

### YAML Configuration File

```yaml
name: production-app
debug: false
workers: 8
```

### Command Line Override

```bash
python app.py name=my-app debug=true workers=16
```

### Environment Variables

```bash
export CONFEE_NAME=my-app
export CONFEE_DEBUG=true
export CONFEE_WORKERS=16

python app.py
```

### Help Display

```bash
python app.py --help
```

### Detailed Validation Error Messages

By default, validation errors are displayed concisely, but using the `--verbose` flag shows detailed error information for each field:

```bash
# Concise error message (default)
python app.py name=123

# Output:
# Config error: field 'name' - Input should be a valid string

# Display detailed error messages in verbose mode
python app.py name=123 --verbose

# Output:
# ❌ Configuration Validation Error
#
#   Found 1 validation error(s):
#
#   [1] Field: name
#       Error: Input should be a valid string
#       Type: string_type
#       Got: 123
#
#   💡 How to fix:
#     1. Add the required field to your configuration file
#     2. Or pass the value via CLI: python main.py name=myapp
#     3. Or set an environment variable: export CONFEE_NAME=myapp
#     4. Check field types match your configuration class
```

Or set via environment variable:

```bash
export CONFEE_VERBOSITY=verbose
python app.py name=123
```

---

## 🎯 Advanced Features

### Nested Configuration

```python
from confee import ConfigBase

class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432

class AppConfig(ConfigBase):
    name: str
    database: DatabaseConfig

# Override nested fields from CLI
# python app.py database.host=prod.db database.port=3306
config = AppConfig.load()
print(config.database.host)  # "prod.db"
```

### File References

```yaml
# config.yaml
name: my-app
api_key: "@file:secrets/api_key.txt"
database_config: "@config:configs/database.yaml"
```

### Custom Environment Prefix

```python
# Use custom prefix instead of CONFEE_
# MYAPP_DEBUG=true instead of CONFEE_DEBUG=true
config = AppConfig.load(env_prefix="MYAPP_")
```

### Custom Source Order

```python
# Control which sources override others
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["cli", "env", "file"]  # CLI highest priority
)
```

### Strict/Non-Strict Modes

```python
# Strict mode (default): Forbid unknown fields
class Config(ConfigBase):
    name: str

# Non-strict mode: Ignore unknown fields
config = Config.load(strict=False)
```

---

## 🆕 New in v0.3.0

### TOML Support

```python
# Load from TOML file
config = AppConfig.load(config_file="config.toml")

# Load from pyproject.toml
from confee import ConfigLoader
data = ConfigLoader.load_pyproject("pyproject.toml", tool_name="myapp")
```

```toml
# config.toml
name = "my-app"
debug = false
workers = 8

[database]
host = "localhost"
port = 5432
```

### Secret Field Masking

```python
from confee import ConfigBase, SecretField

class AppConfig(ConfigBase):
    name: str
    api_key: str = SecretField(default="")
    database_password: str = SecretField()

config = AppConfig(name="app", api_key="secret123", database_password="pwd")

# Safe output masks secrets
print(config.to_safe_dict())
# {'name': 'app', 'api_key': '***MASKED***', 'database_password': '***MASKED***'}

config.print(safe=True)  # Pretty print with masked secrets
```

### Config Freezing

```python
config = AppConfig.load(config_file="config.yaml")

# Freeze to prevent modifications
config.freeze()
config.name = "new"  # Raises AttributeError

# Check frozen state
if config.is_frozen():
    config = config.copy_unfrozen()  # Create mutable copy
    config.name = "new"
```

### JSON Schema Export

```python
from confee import SchemaGenerator

# Generate JSON Schema
schema = AppConfig.to_json_schema()
AppConfig.save_schema("config.schema.json")

# Validate data against schema
from confee import SchemaValidator
validator = SchemaValidator(AppConfig)
is_valid = validator.validate({"name": "app", "workers": 4})
```

### Async Config Loading

```python
from confee import AsyncConfigLoader

async def main():
    # Load local file (static method - no instantiation needed)
    config = await AsyncConfigLoader.load_as("config.yaml", AppConfig)
    
    # Load from URL (requires aiohttp) - returns dict
    data = await AsyncConfigLoader.load_remote("https://example.com/config.yaml")
    
    # Watch for file changes
    async def on_change(old_config, new_config):
        print("Config changed:", new_config)
    
    watcher = await AsyncConfigLoader.watch("config.yaml", on_change)
    # ... application runs ...
    await watcher.stop()
```

### Plugin System

```python
from confee import PluginRegistry

# Register custom loader
@PluginRegistry.loader(".ini")
def load_ini(path: str) -> dict:
    import configparser
    parser = configparser.ConfigParser()
    parser.read(path)
    return {s: dict(parser[s]) for s in parser.sections()}

# Now .ini files are automatically supported
config = AppConfig.load(config_file="config.ini")
```

### Config Diff & Merge

```python
config1 = AppConfig(name="app1", workers=4)
config2 = AppConfig(name="app2", workers=8)

# Compare configurations
diff = config1.diff(config2)
# {'name': ('app1', 'app2'), 'workers': (4, 8)}

# Merge configurations
merged = config1.merge(config2)  # config2 values take precedence
```

---

## 📚 Documentation

- [Comparison with OmegaConf](./comparison.md)
- [Development Guide](./development.md)
- [License](./license)

---

## 🎯 Use Cases

### Environment-specific Configuration

```python
# dev.yaml
debug: true
workers: 2

# prod.yaml
debug: false
workers: 32

# Load appropriate config
import os
env = os.getenv("APP_ENV", "dev")
config = AppConfig.load(config_file=f"{env}.yaml")
```

### Kubernetes Environment Variables

```yaml
# pod.yaml
containers:
  - env:
    - name: CONFEE_DEBUG
      value: "false"
    - name: CONFEE_WORKERS
      value: "16"
```

### Configuration Validation

```python
from pydantic import Field

class AppConfig(ConfigBase):
    workers: int = Field(ge=1, le=128)  # Validate range
    timeout: float = Field(gt=0)         # Must be positive
```

---

## 🔄 Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
from confee import ConfigBase

class AppConfig(ConfigBase):
    title: str = "My API"
    debug: bool = False

# Load config from file and environment only (no CLI)
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["env", "file"]
)
app = FastAPI(title=config.title, debug=config.debug)
```

### With Click

```python
import click
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str

# Load config from file and environment only (no CLI)
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["env", "file"]
)

@click.command()
def main():
    click.echo(f"Hello {config.name}")
```

---

## ✅ Testing Your Configuration

```python
def test_config_loading():
    config = AppConfig.load(
        config_file="tests/fixtures/config.yaml",
        cli_args=["debug=true"],
        strict=True
    )
    assert config.debug is True
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Submit a pull request

---

## 📜 License

MIT License © 2025

See [LICENSE](./license) for details.

---

## 💬 Support

For issues and questions:
- GitHub Issues: https://github.com/bestend/confee/issues
- GitHub Discussions: https://github.com/bestend/confee/discussions

---

**Enjoy ☕️ configuration management!**

---

**Language:** [한국어](./readme.ko.md) | English

