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

**confee** makes configuration management simple, type-safe, and intuitive. Combine config files, Pydantic validation, environment variables, and CLI arguments seamlessly.

---

## ✨ Features

- **🎯 Type-Safe** — Pydantic V2 validation & IDE autocomplete
- **📋 Multi-Format** — YAML, JSON, TOML auto-detection
- **🔄 Override System** — CLI args & environment variables with priority control
- **🔐 Secret Masking** — `SecretField()` for sensitive data
- **🧊 Immutability** — Runtime config freezing
- **📐 Extensible** — Plugin system, JSON Schema, async loading

---

## 📦 Installation

```bash
pip install confee
```

---

## 🚀 Quick Start

```python
from confee import ConfigBase, SecretField

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4
    api_key: str = SecretField(default="")

config = AppConfig.load(config_file="config.yaml")
print(config.name)  # Type-safe access
```

```yaml
# config.yaml
name: my-app
workers: 8
api_key: secret123
```

```bash
# Override via CLI
python app.py name=production debug=true

# Override via environment
export CONFEE_NAME=production
```

---

## 💡 Common Patterns

### Nested Configuration

```python
class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432

class AppConfig(ConfigBase):
    database: DatabaseConfig

# Override: python app.py database.host=prod.db
```

### File References & Secret Masking

```yaml
api_key: "@file:secrets/api_key.txt"
```

```python
config.to_safe_dict()  # {'api_key': '***MASKED***', ...}
```

### Config Freezing & Custom Prefix

```python
config = AppConfig.load(
    config_file="config.yaml",
    env_prefix="MYAPP_",
    strict=False
)
config.freeze()  # Immutable
```

---

## 📚 Documentation

For advanced features, see [ADVANCED.md](./ADVANCED.md):
- Config Freezing & Immutability
- JSON Schema Generation
- Remote Config Loading (HTTP/HTTPS)
- Plugin System (Custom Loaders, Validators, Hooks)
- Config Diff & Merge
- Integration Examples (FastAPI, Django, Kubernetes, AWS Lambda)

---

## 📄 License

MIT License © 2025 — See [LICENSE](./LICENSE) for details.
