<p align="center">
  <img src="https://raw.githubusercontent.com/bestend/confee/main/assets/logo.png" width="360" />
</p>

<div align="center">

**Language:** [한국어](./README.ko.md) | English

Hydra-style Configuration + Pydantic Type Safety + Auto Help Generation

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bestend/confee/actions/workflows/tests.yml/badge.svg)](https://github.com/bestend/confee/actions/workflows/tests.yml)

</div>

---

## ☕️ Overview

**confee** makes configuration management in Python simple, type-safe, and intuitive. Combine Hydra-style config files, Pydantic validation, environment variables, and CLI arguments seamlessly.

---

## ✨ Features

- **🎯 Type-Safe** — Pydantic V2 validation & IDE autocomplete
- **📋 Multi-Format** — YAML, JSON, TOML auto-detection
- **🔄 Override System** — CLI args & environment variables
- **🔐 Secret Masking** — `SecretField()` for sensitive data
- **🧊 Config Freezing** — Runtime immutability
- **📐 JSON Schema** — Export & validate schemas
- **⚡ Async Loading** — Non-blocking I/O with file watching
- **🔌 Plugin System** — Custom format loaders
- **💬 Auto Help** — `--help` flag support

---

## 📦 Installation

```bash
pip install confee

# Optional features
pip install confee[remote]  # Async remote loading
pip install confee[all]     # All features
```

---

## 🚀 Quick Start

```python
from confee import ConfigBase, SecretField

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4
    api_key: str = SecretField(default="")  # Masked in output

config = AppConfig.load(config_file="config.yaml")
print(config.name)  # Type-safe access with IDE support
```

```yaml
# config.yaml
name: my-app
debug: false
workers: 8
api_key: secret123
```

```bash
# Override via CLI
python app.py name=production debug=true

# Override via environment
export CONFEE_NAME=production
export CONFEE_DEBUG=true
```

---

## 🎯 Advanced Usage

### Nested Configuration

```python
class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432

class AppConfig(ConfigBase):
    name: str
    database: DatabaseConfig

# Override nested fields: python app.py database.host=prod.db
```

### File References

```yaml
api_key: "@file:secrets/api_key.txt"
database: "@config:configs/database.yaml"
```

### Secret Masking

```python
config.to_safe_dict()  # {'api_key': '***MASKED***', ...}
config.print(safe=True)  # Pretty print with masked secrets
```

### Config Freezing

```python
config.freeze()
config.name = "new"  # Raises AttributeError

# Create mutable copy
unfrozen = config.copy_unfrozen()
```

### JSON Schema

```python
schema = AppConfig.to_json_schema()
AppConfig.save_schema("config.schema.json")
```

### Remote Config

```python
# Sync (stdlib urllib)
data = ConfigLoader.load_remote("https://example.com/config.yaml")

# Async (requires aiohttp)
data = await AsyncConfigLoader.load_remote("https://example.com/config.yaml")
```

### Plugin System

```python
from confee import PluginRegistry

@PluginRegistry.loader(".ini")
def load_ini(path: str) -> dict:
    import configparser
    parser = configparser.ConfigParser()
    parser.read(path)
    return {s: dict(parser[s]) for s in parser.sections()}
```

### Config Diff & Merge

```python
diff = config1.diff(config2)  # {'name': ('app1', 'app2')}
merged = config1.merge(config2)  # config2 takes precedence
```

---

## ⚙️ Configuration Options

```python
config = AppConfig.load(
    config_file="config.yaml",
    env_prefix="MYAPP_",  # Custom env prefix
    source_order=["cli", "env", "file"],  # Priority order
    strict=False,  # Allow unknown fields
)
```

---

## 🔄 Integration

### FastAPI

```python
config = AppConfig.load(config_file="config.yaml", source_order=["env", "file"])
app = FastAPI(title=config.name, debug=config.debug)
```

### Kubernetes

```yaml
env:
  - name: CONFEE_DEBUG
    value: "false"
  - name: CONFEE_WORKERS
    value: "16"
```

---

## 📄 License

MIT License © 2025 — See [LICENSE](./LICENSE) for details.

---

**Enjoy ☕️ configuration management!**
