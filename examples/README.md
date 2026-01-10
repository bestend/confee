# confee Examples ☕️

This directory contains practical examples demonstrating how to use confee in various scenarios.

## 📋 Available Examples

| Example | Description | Complexity |
|---------|-------------|------------|
| `01_basic_usage.py` | Getting started with basic configuration | ⭐ Beginner |
| `02_cli_overrides.py` | Override config values from command line | ⭐⭐ Intermediate |
| `03_secrets.py` | Managing sensitive data with SecretField | ⭐⭐ Intermediate |
| `04_fastapi.py` | Integration with FastAPI framework | ⭐⭐⭐ Advanced |

## 🚀 Running Examples

Each example is self-contained and can be run directly:

```bash
# Basic usage
python examples/01_basic_usage.py

# CLI overrides
python examples/02_cli_overrides.py debug=true workers=8

# Secrets management
python examples/03_secrets.py

# FastAPI integration (requires: pip install fastapi uvicorn)
python examples/04_fastapi.py
```

## 📁 Example Config Files

Most examples reference configuration files in the `configs/` subdirectory:

```
examples/
├── README.md
├── 01_basic_usage.py
├── 02_cli_overrides.py
├── 03_secrets.py
├── 04_fastapi.py
└── configs/
    ├── app.yaml
    ├── database.yaml
    └── secrets.yaml
```

## 💡 What to Learn

### 01_basic_usage.py
- Loading YAML/JSON/TOML config files
- Type-safe configuration with Pydantic
- IDE autocomplete support
- Basic validation

### 02_cli_overrides.py
- Command-line argument parsing
- Environment variable overrides
- Priority order (CLI > env > file)
- Nested field overrides

### 03_secrets.py
- Using `SecretField()` for sensitive data
- Masking secrets in outputs (`to_safe_dict()`)
- Safe printing vs unsafe printing
- Loading secrets from files

### 04_fastapi.py
- FastAPI application configuration
- Environment-based config selection
- Config validation at startup
- Dependency injection patterns

## 📚 Additional Resources

- [Main README](../README.md) - Full documentation
- [CONTRIBUTING](../CONTRIBUTING.md) - Development guide
- [ARCHITECTURE](../ARCHITECTURE.md) - System design

## 🆘 Need Help?

If you have questions about any example:
1. Read the inline comments in the example file
2. Check the [main documentation](../README.md)
3. Open a [GitHub Discussion](https://github.com/bestend/confee/discussions)

---

**Enjoy ☕️ configuration management!**
