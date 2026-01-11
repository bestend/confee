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

```yaml
# config.yaml
name: my-app
debug: false
workers: 4
```

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4

config = AppConfig.load("config.yaml")
print(f"App: {config.name}, Workers: {config.workers}")
```

```bash
# Override with CLI args
python app.py debug=true workers=8

# Override with environment variables
CONFEE_WORKERS=16 python app.py
```

### Auto-Generated Help

Run with `--help` to see available options:

```bash
$ python app.py --help
```

```
Usage: app.py [OPTIONS]

Options:
  --name     str   name
  --debug    bool  debug [default: False]
  --workers  int   workers [default: 4]

Override format:
  key=value              Set a simple value
  nested.key=value       Set a nested value
  @file:path/to/file     Read value from file
  true/false/yes/no/on/off for boolean values

Examples:
  app.py debug=true workers=8
  app.py --help
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

config = AppConfig.load("config.yaml")
```

```bash
python app.py database.host=prod.db database.port=3306
```

### Config Freezing

```python
config = AppConfig.load("config.yaml")
config.freeze()

try:
    config.name = "changed"
except AttributeError:
    print("Config is frozen!")
```

---

## 📚 Documentation

**See [examples/](./examples/) for more:**
- `01_basic_usage.py` - Type-safe config, freezing
- `02_cli_overrides.py` - CLI args & env vars
- `03_secrets.py` - SecretField & masking
- `04_fastapi.py` - FastAPI integration

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
